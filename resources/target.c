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




/*
void memset(int buffer[],int value,int size){
  int index;
  index=0;
  while(index<size){
    buffer[index]=value;
    index =index+1;
  }
}
int s;
int fabBuffer[100];


int fab(int n){
  int temp;
  if(n==0) return 0;
  if(n==1) return 1;
  if(fabBuffer[n]!=0) return fabBuffer[n];
  temp= fab(n-1)+fab(n-2);
  fabBuffer[n]=temp;

  return temp;
}

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
}*/

/*
int x[10];
int minloc ( int a[], int low, int high )
{
  int i; int x; int k;
  k = low;
  x = a[low];
  i = low + 1;
  while (i < high)
  {
    if (a[i] < x)
    {
      x = a[i];
      k = i;
    }
    i = i + 1;
  }
  return k;
}
void sort ( int a[], int low, int high )
{
  int i; int k;
  i = low;
  while (i < high-1)
  {
   int t;
   k = minloc (a,i,high);
   t =a[k];
   a[k] = a[i];
   a[i] = t;
   i = i + 1;
  }
}

int func(){
}
void main (void)
{
  int i;
  i = 0;
  while (i < 10)
  {

     x[i]=input();

     i = i + 1;
  }
     sort (x,0,10);
     i = 0;
  while (i < 10)
   {
     output(x[i]);
     i = i + 1;
   }
}*/


int gcd (int u, int v)
{
if (v == 0)
 return u ;
else
 return gcd(v,u-u/v*v);
/* u-u/v*v == u mod v */
}
void main(void)
{
output(123+231*3/0+123);
int x;
int y;
x = input();
y = input();
  output(gcd(x,y));


}