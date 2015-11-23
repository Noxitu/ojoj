#include <unistd.h>
#include <fcntl.h>

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>

#include <cstdio>
#include <cstdlib>
#include <cmath>

void limit(int res, rlim_t val, rlim_t hval) {
	rlimit rlim;
	rlim.rlim_cur = val;
	rlim.rlim_max = hval;
	setrlimit( res, &rlim );
}

void limit(int res, rlim_t val) { limit(res, val, val); }

enum OJOJ_JUDGE_RETURN_CODE {
	OJOJ_JUDGE_OK = 0,
	OJOJ_JUDGE_TLE = 1,
	OJOJ_JUDGE_RE = 3,
	OJOJ_JUDGE_NZEC = 4,
	OJOJ_JUDGE_INTERNAL_ERROR = 44
};

int main( int argc, char **argv, char **arge ){
	if( argc != 6 ) {
		fprintf(stderr, "Not enough args!\n./ojoj_judge application cpu_limit(sec) mem_limit(kB) input_path output_path\n");
		return OJOJ_JUDGE_INTERNAL_ERROR;
	}
	char *path = argv[1];								// Application path
	float cpu_limit_f; sscanf(argv[2], "%f", &cpu_limit_f); // Cpu time limit (float)
	int cpu_limit = (int) ceil(cpu_limit_f);					// Cpu time limit (sec)
	int mem_limit = atoi(argv[3])*1024;					// Memory limit (kB)
	int input_fd = open( argv[4], O_RDONLY );				// Input descriptor
	int output_fd = open( argv[5], O_WRONLY bitor O_TRUNC bitor O_CREAT, 0600 );	// Output descriptor
	int error_fd  = open( "/dev/null", O_WRONLY ); 		// No stderr for app


	// Subprocess launching the app
	pid_t tested_pid = fork();
	if( not tested_pid ) {
		chdir("/tmp");
		dup2( input_fd, 0 );			// Replace stdin with input
		dup2( output_fd, 1 );			// Replace stdout with output
		dup2( error_fd, 2 );			// Replace stderr with error_fd

		limit( RLIMIT_CPU, cpu_limit, cpu_limit+1 );
		limit( RLIMIT_AS, mem_limit );
#ifdef RLIMIT_NPROC
		limit( RLIMIT_NPROC, 0);				// No forks
#else
  #warning "No RLIMIT_NPROC in os, processes can fork!"
#endif
		limit( RLIMIT_FSIZE, 32*1024*1024); 	// 32 MB output file limit
//		limit( RLIMIT_NOFILE, 0);				// FAILS WHILE LOADING stdlib - do it using entry point

		char *argv[] = { path, NULL };
		char *arge[] = { NULL };

		execve( path, argv, arge );		// Execve wont return here

		return OJOJ_JUDGE_INTERNAL_ERROR;
	}

	// Add sleeping subprocess in case of some endless app that doesn't consume CPU
	pid_t sleeper_pid = fork();
	if( not sleeper_pid ) {
		sleep( cpu_limit*2 + 2 );		// Time after we expect app to end
		kill( tested_pid, SIGXCPU );
		sleep( 1 );
		kill( tested_pid, SIGKILL );
		return 0;
	}

	int status;								// App status
	rusage usage;							// App usage 

	// Wait for app to terminate:
	wait4( tested_pid, &status, WUNTRACED, &usage );
	close( output_fd );
	// Kill sleeper
	kill(sleeper_pid, SIGKILL);

	// Get subprocess resource usage
	float cpu_used = usage.ru_utime.tv_sec + 1e-6 * usage.ru_utime.tv_usec;
	long  mem_used = usage.ru_maxrss;
	printf("%f %ld\n", cpu_used, mem_used );
	fprintf( stderr, "CPU: %.3f sec\nMemory: %ld kB\n", cpu_used, mem_used );

	// Verify
    if( not WIFEXITED(status) ) {
        switch( WTERMSIG(status) ) {
            case SIGXCPU:
                return OJOJ_JUDGE_TLE;

            case SIGABRT: // 6: typicaly assertion fail inside new operator on MLE
            case SIGSEGV: // 11: sometimes MLE
            default:
                return OJOJ_JUDGE_RE;
        }
    }
    
    if( WEXITSTATUS(status) != 0 )
        return OJOJ_JUDGE_NZEC;

	if( mem_used > mem_limit )
		return OJOJ_JUDGE_RE;

    if( cpu_used > cpu_limit_f )
		return OJOJ_JUDGE_TLE;
        
    return OJOJ_JUDGE_OK;
}	
