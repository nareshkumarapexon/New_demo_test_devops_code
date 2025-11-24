"""
UseCase Agent for Neptune batch-load workflows (permission checks + orchestration)

Requirements:
  - boto3
  - AWS credentials configured in environment (profile, env vars, or instance role)

What to customize:
  - GRAPH_ARN: your Neptune Analytics graph ARN (or set to None if checking neptune-db)
  - S3_BUCKET and S3_PREFIX: where your CSV files live
  - batch_load() implementation: call your actual Neptune load API here
  - generate_csvs() implementation: if you already generate CSVs, you can skip or adapt

Run: python usecase_agent.py
"""

import boto3
import botocore
import logging
import time
from typing import List, Optional, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("UseCaseAgent")


class UseCaseAgent:
    def __init__(self,
                 principal_arn: str,
                 s3_bucket: str,
                 s3_prefix: str = "",
                 graph_arn: Optional[str] = None,
                 neptune_mode: str = "graph"  # "graph" or "db"
                 ):
        """
        principal_arn: ARN of role/user that will execute step 4 (e.g. Lambda execution role ARN)
        s3_bucket: name of S3 bucket containing CSVs
        s3_prefix: optional prefix/path for CSVs
        graph_arn: Neptune Analytics graph ARN (if using Neptune Analytics). If using classic cluster, set None.
        neptune_mode: "graph" -> use neptune-graph: actions; "db" -> use neptune-db: actions
        """
        self.principal_arn = principal_arn
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix.strip("/")
        self.graph_arn = graph_arn
        self.neptune_mode = neptune_mode

        self.iam = boto3.client("iam")
        self.s3 = boto3.client("s3")
        self.sts = boto3.client("sts")

        # choose action prefixes based on mode
        if neptune_mode == "graph":
            self.prefix = "neptune-graph"
        elif neptune_mode == "db":
            self.prefix = "neptune-db"
        else:
            raise ValueError("neptune_mode must be 'graph' or 'db'")

        # actions to simulate
        self.neptune_actions = [
            f"{self.prefix}:ReadDataViaQuery",
            f"{self.prefix}:WriteDataViaQuery",
            f"{self.prefix}:DeleteDataViaQuery"
        ]
        self.s3_actions = ["s3:GetObject", "s3:ListBucket"]

    def simulate_permissions(self, actions: List[str], resource_arns: List[str]) -> Dict:
        """
        Use IAM SimulatePrincipalPolicy to check whether the principal_arn allows the requested actions on resources.
        Returns the raw simulation response dict.
        """
        logger.info("Simulating permissions for %s", self.principal_arn)
        try:
            resp = self.iam.simulate_principal_policy(
                PolicySourceArn=self.principal_arn,
                ActionNames=actions,
                ResourceArns=resource_arns
            )
            return resp
        except botocore.exceptions.ClientError as e:
            logger.error("SimulatePrincipalPolicy failed: %s", e)
            raise

    def check_neptune_permissions(self) -> bool:
        """Simulate Neptune actions against the graph ARN (if provided)."""
        if not self.graph_arn:
            logger.warning("No graph ARN provided; skipping graph-scoped simulation. You may be using a cluster-based flow.")
            # You may opt to simulate using a wildcard resource if desired:
            resource_arns = ["*"]
        else:
            resource_arns = [self.graph_arn]

        resp = self.simulate_permissions(self.neptune_actions, resource_arns)
        denied = []
        for r in resp.get("EvaluationResults", []):
            action = r.get("EvalActionName")
            decision = r.get("EvalDecision")
            if decision != "allowed":
                denied.append((action, decision, r.get("MatchedStatements", [])))
        if denied:
            logger.error("Neptune permission simulation shows DENIED actions: %s", denied)
            return False
        logger.info("Neptune permission simulation OK (all required actions allowed).")
        return True

    def check_s3_permissions(self) -> bool:
        """Simulate S3 permissions and do a quick read attempt on the bucket/prefix."""
        # Resources for simulation: bucket and objects under prefix
        bucket_arn = f"arn:aws:s3:::{self.s3_bucket}"
        object_arn = f"arn:aws:s3:::{self.s3_bucket}/{self.s3_prefix}/*" if self.s3_prefix else f"arn:aws:s3:::{self.s3_bucket}/*"
        try:
            resp = self.simulate_permissions(self.s3_actions, [bucket_arn, object_arn])
        except botocore.exceptions.ClientError:
            return False

        denied = []
        for r in resp.get("EvaluationResults", []):
            if r.get("EvalDecision") != "allowed":
                denied.append((r.get("EvalActionName"), r.get("EvalDecision")))
        if denied:
            logger.error("S3 permission simulation shows DENIED actions: %s", denied)
            return False

        # Also attempt a minimal S3 call (list objects) to catch bucket policy / KMS issues
        try:
            list_kwargs = {"Bucket": self.s3_bucket, "MaxKeys": 1}
            if self.s3_prefix:
                list_kwargs["Prefix"] = self.s3_prefix
            logger.info("Attempting S3 ListObjectsV2 on bucket to validate access...")
            self.s3.list_objects_v2(**list_kwargs)
            logger.info("S3 access check OK.")
            return True
        except botocore.exceptions.ClientError as e:
            logger.error("S3 call failed: %s", e)
            return False

    def generate_csvs(self) -> bool:
        """
        Stub: run step 1-3 of your workflow (CSV creation/enrichment).
        Replace this with your real implementation or call out to your existing step.
        """
        logger.info("Running CSV generation step (stub)...")
        # simulate some activity
        time.sleep(1)
        # Write: if you want, upload a small file to S3 to simulate presence
        # self.s3.put_object(Bucket=self.s3_bucket, Key=f"{self.s3_prefix}/_agent_test.csv", Body="id\n1\n")
        logger.info("CSV generation completed (stub). CSVs should be in s3://%s/%s", self.s3_bucket, self.s3_prefix)
        return True

    def batch_load(self) -> bool:
        """
        Stub: perform the actual Neptune batch load.
        Replace this with your actual call: e.g. use Neptune Data API, Gremlin call, or call neptune.load equivalent.
        Return True on success, False on failure.
        """
        logger.info("Starting batch load step (stub). Replace this method with actual Neptune load call.")
        # Example: your load call might be a signed HTTP request to Neptune Data API,
        # or using a specialized client. Keep the check that the principal has the required perms.
        time.sleep(1)
        # Simulate success
        logger.info("Batch load simulated as SUCCESS (replace with real call).")
        return True

    def run(self) -> Dict:
        """
        Full run: checks -> CSV generation -> batch load
        Returns a summary dict with step results.
        """
        summary = {
            "identify_principal": {"ok": True, "principal_arn": self.principal_arn},
            "check_neptune_permissions": {"ok": False},
            "check_s3_permissions": {"ok": False},
            "generate_csvs": {"ok": False},
            "batch_load": {"ok": False}
        }

        # 1) Neptune permission check
        try:
            ok_neptune = self.check_neptune_permissions()
            summary["check_neptune_permissions"]["ok"] = ok_neptune
        except Exception as e:
            summary["check_neptune_permissions"]["error"] = str(e)
            logger.exception("Error while checking Neptune permissions")
            return summary

        # 2) S3 permission check
        try:
            ok_s3 = self.check_s3_permissions()
            summary["check_s3_permissions"]["ok"] = ok_s3
            if not ok_s3:
                logger.error("S3 permissions check failed; aborting before CSV generation/batch load.")
                return summary
        except Exception as e:
            summary["check_s3_permissions"]["error"] = str(e)
            logger.exception("Error while checking S3 permissions")
            return summary

        # 3) Generate CSVs (steps 1-3)
        try:
            ok_gen = self.generate_csvs()
            summary["generate_csvs"]["ok"] = ok_gen
            if not ok_gen:
                logger.error("CSV generation failed; aborting.")
                return summary
        except Exception as e:
            summary["generate_csvs"]["error"] = str(e)
            logger.exception("Error while generating CSVs")
            return summary

        # 4) Batch load
        if not summary["check_neptune_permissions"]["ok"]:
            logger.error("Neptune permissions insufficient; cannot perform batch load.")
            return summary

        try:
            ok_load = self.batch_load()
            summary["batch_load"]["ok"] = ok_load
            if not ok_load:
                logger.error("Batch load failed (see logs).")
            else:
                logger.info("Workflow completed successfully.")
        except Exception as e:
            summary["batch_load"]["error"] = str(e)
            logger.exception("Error during batch load")
        return summary


if __name__ == "__main__":
    # Example usage - change values below
    # principal_arn: the ARN of the role or user that will run step 4 (Lambda role ARN, or user ARN)
    # For example: arn:aws:iam::123456789012:role/my-lambda-role
    principal_arn = "arn:aws:iam::123456789012:role/YourLambdaExecutionRole"
    s3_bucket = "your-csv-bucket-name"
    s3_prefix = "neptune/csvs"
    # If you're using Neptune Analytics, set the graph ARN; otherwise set to None.
    graph_arn = "arn:aws:neptune-graph:us-east-1:123456789012:graph/g-abcdefgh"  # or None for cluster-mode
    agent = UseCaseAgent(principal_arn=principal_arn,
                         s3_bucket=s3_bucket,
                         s3_prefix=s3_prefix,
                         graph_arn=graph_arn,
                         neptune_mode="graph")
    summary = agent.run()
    print("\nSUMMARY:")
    for k, v in summary.items():
        print(f"- {k}: {v}")
