print("Arithmetic Calculations: \n")

def sum_it(a,b):
    return a+b

def subtraction(a,b):
    return a-b

def multiplication(a,b):
    return a*b

def division(a,b):
    if a==0 or b==0:
        return f"Not divisible because '0' is in denomenator"
    else:
        return a/b
a=int(input("Enter the value a = "))
b=int(input("Enter the value b = "))
print("\nKindly enter only below options")
print("\n 1 = Addition \n 2 = Subtraction \n 3 = Multiplication \n 4 = Division")
s= int(input("\n Enter the Arithmetic opertion: " ))

if s==1:
    print(f"Result:{a}+{b} =",sum_it(a,b))
elif s==2:
    print(f"Result:{a}-{b} =",subtraction(a,b))
elif s==3:
    print(f"Result:{a}*{b} =",multiplication(a,b))
elif s==4:
    print(f"Result:{a}/{b} =",division(a,b))
else:
    print("Enter only assgined number for Arithmetic opertion that mentioned above:-).")