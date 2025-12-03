def sum_it(a,b):
    return a+b

def substract(a,b):
    return a-b

def mult(a,b):
    return a*b

def dev(a,b):
    if b==0:
        return f"Not divisible because 0 is in denomenator"
    else:
        return a/b

a=int(input("Enter 'a' value: "))
b=int(input("Enter 'b' value: "))
print("Choose following options")
print("\n 1 for adding \n 2 for subs \n 3 for mult \n 4 for divis")

s=int(input("\nEnter the Value: "))
if s==1:
    print(sum_it(a,b))
elif s==2:
    print(substract(a,b))
elif s==3:
    print(mult(a,b))

elif s==4:
    print(dev(a,b))
else:
    print("Enter number only that mentioned above:")