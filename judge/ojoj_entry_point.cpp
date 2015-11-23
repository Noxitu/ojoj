#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <iostream>

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>

void limit(int res, rlim_t val) {
	struct rlimit rlim;
	rlim.rlim_cur = val;
	rlim.rlim_max = val;
	setrlimit( res, &rlim );
}

int ojoj_entry_point() {
	limit(RLIMIT_NOFILE, 0);
	//limit(RLIMIT_FSIZE, 0);
}

static int ojoj_void_var( ojoj_entry_point() );
