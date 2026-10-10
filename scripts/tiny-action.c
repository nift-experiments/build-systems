/* Intentionally tiny deterministic file transformation, not a compiler. */
#include <stdio.h>
int main(int argc,char **argv){
 if(argc!=3)return 64;
 FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");
 if(!in||!out)return 65;
 unsigned long long h=1469598103934665603ULL;int c;
 while((c=fgetc(in))!=EOF){h^=(unsigned char)c;h*=1099511628211ULL;}
 if(ferror(in)||fprintf(out,"%016llx\n",h)<0)return 66;
 fclose(in);return fclose(out)!=0;
}
