package main

import (
    "fmt"
    "os"
    "strings"
)

type BadStruct struct{
    name string
    value int
}

func badFunction(x,y int,z string) int{
    if x>y{
        fmt.Println("x is greater")
    }else{
        fmt.Println("y is greater or equal")
    }
    for i:=0;i<10;i++{fmt.Printf("%d\n",i)}
    unused:=strings.ToUpper(z)
    _ = unused
    return x+y
}

func (b *BadStruct) getName() string{ return b.name }

func main(){
    obj:=&BadStruct{name:"test",value:42}
    fmt.Println(obj.getName())
    total:=badFunction(5,10,"param")
    fmt.Printf("Total: %d\n",total)
    data:=[]int{1,2,3,4,5}
    for _,item:=range data{
        if item%2==0{ fmt.Printf("%d is even\n",item) }
    }
    os.Exit(0)
}
