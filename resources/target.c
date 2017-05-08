/*
这里是冒泡排序
void sort(int x[],int n){
   int i;
   int j;
   i=0;
   while(i<n){
    j=i;
    while(j<n-1){
      if (x[i]>x[j+1]){
        int temp;
        temp =x[i];
        x[i]=x[j+1];
        x[j+1]=temp;
      }
      j=j+1;
    }
    i=i+1;
   }
}

void print(int x[], int n){
  int i;
  while(i<n){
    output(x[i]);
    i=i+1;
  }
}

void main(){
  int x[4];
  x[0]=8;
  x[1]=2;
  x[2]=1;
  x[3]=7;
  sort(x,4);
  print(x,4);

}*/

/*输入测试
void main(){

   int x;
   x= input();
   output(x);
}*/

/*
求和运算
int sum(int a[],int n){
    int total;
    total =0;
    int i;
    i=0;
    while(i<n){
    total=a[i]+total;
    i=i+1;
    }
    return total;
}
void main()
{
  int a[4];
  a[0]=1;
  a[1]=2;
  a[2]=3;
  a[3]=4;

  output(sum(a,4));
}*/



/*设置某个数组的值*/
void memset(int buffer[],int value,int size){
  int index;
  index=0;
  while(index<size){
    buffer[index]=value;
    index =index+1;
  }
}
int s; /*全局变量s*/
int fabBuffer[100]; /*斐波那契数列的buffer*/

/*递归的斐波那契数列计算*/
int fab(int n){
  int temp;
  if(n==0) return 0;
  if(n==1) return 1;
  if(fabBuffer[n]!=0) return fabBuffer[n];
  temp= fab(n-1)+fab(n-2);
  fabBuffer[n]=temp;

  return temp;
}
/*斐波那契测试函数*/
void fabTest(int n){

  memset(fabBuffer,0,100);

  int index;
  index=1;
  while(index<n){
       output(fab(index));
       index=index+1;
  }
}

void main(){
  fabTest(100);
  s=input();
  output(s);
}
