/* Common measurement instrumentation, never a scheduler or dirty checker. */
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
int main(int argc,char **argv) {
    if(argc<3) return 64;
    const char *trace=getenv("BUILD_TRACE");
    if(trace) {
        int fd=open(trace,O_WRONLY|O_CREAT|O_APPEND,0600);
        if(fd<0) {perror("trace open");return 65;}
        size_t n=strlen(argv[1]);char *line=malloc(n+2);
        if(!line) return 66;
        memcpy(line,argv[1],n);line[n]='\n';
        ssize_t wrote=write(fd,line,n+1);close(fd);free(line);
        if(wrote!=(ssize_t)(n+1)) return 67;
    }
    execvp(argv[2],argv+2);perror("execvp");return 127;
}
