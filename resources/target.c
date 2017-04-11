
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
  int x[10];
  x[0]=8;
  x[1]=2;
  x[2]=1;
  x[3]=7;
  sort(x,4);
  print(x,4);
}