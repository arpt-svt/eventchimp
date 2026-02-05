import os,sys,json

def bad_function(x,y,z=None):
    if x>y:
        print("x is greater")
    else:
        print("y is greater or equal")
    for i in range(10): print(i)
    return x+y

class badclass:
    def __init__(self,name,value):
        self.name=name
        self.value=value

    def get_name(self):
        return self.name

    def calculate(self,a,b,c):
        result=a+b*c
        return result

def main():
    obj=badclass("test",42)
    print(obj.get_name())
    total=bad_function(5,10)
    print(f"Total: {total}")
    data=[1,2,3,4,5]
    for item in data:
        if item%2==0:
            print(f"{item} is even")

if __name__=="__main__":
    main()
