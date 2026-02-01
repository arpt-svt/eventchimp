#include <iostream>
#include <vector>
#include <string>

using namespace std;

class BadClass{
    private:
        int x;
        string name;
    public:
        BadClass(int x,string name){
            this->x=x;
            this->name=name;
        }

        int getX(){ return x; }

        string getName(){ return name; }

        int calculate(int a,int b,int c){ return a+b*c; }
};

void badFunction(int x,int y,string z="default"){
    if(x>y){
        cout<<"x is greater"<<endl;
    }else{
        cout<<"y is greater or equal"<<endl;
    }
    for(int i=0;i<10;i++){ cout<<i<<endl; }
}

int main(){
    BadClass obj(42,"test");
    cout<<obj.getName()<<endl;
    int unused=0;
    badFunction(5,10);
    vector<int> data{1,2,3,4,5};
    for(int item:data){
        if(item%2==0){
            cout<<item<<" is even"<<endl;
        }
    }
    return 0;
}
