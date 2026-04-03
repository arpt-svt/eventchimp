import java.util.List;
import java.util.ArrayList;

public class Test {
    private int x=1;private String name="test";

    public void badMethod(){
        int a=5;
        int b=10;
        int unused=0;
        if(a<b)
            System.out.println("a is less than b");
        for(int i=0;i<10;i++){System.out.println(i);}
    }

    public int getX(){ return x; }

    public void setX(int x){ this.x=x; }

    public static void main(String args[]){
        Test t=new Test();
        t.badMethod();
        System.out.println(t.getX());
    }
}

class AnotherClass{
    private int value;

    public AnotherClass(int v){ value=v; }

    public int getValue(){ return value; }
}