#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>
#include <unistd.h>

#define check(X) if ((X) == -1) { perror(#X); exit(1); }

static const char *namespaces[] = {
	"ipc",
	"mnt",
	"net",
	"time",
	"uts",
};

static const int num_namespaces = sizeof(namespaces) / sizeof(namespaces[0]);

static void host_nsenter()
{
	int proc_fs_fd;
	int proc_fd;
	int proc_ns_fd;
	int ns_fd;

	check(proc_fs_fd = fsopen("proc", 0));
	check(fsconfig(proc_fs_fd, FSCONFIG_SET_STRING, "subset", "pid", 0));
	check(fsconfig(proc_fs_fd, FSCONFIG_CMD_CREATE, NULL, NULL, 0));
	check(proc_fd = fsmount(proc_fs_fd, 0, 0));
	close(proc_fs_fd);

	check(proc_ns_fd = openat(proc_fd, "1/ns", O_RDONLY | O_DIRECTORY));
	close(proc_fd);

	for (size_t i = 0; i < num_namespaces; i++) {
		check(ns_fd = openat(proc_ns_fd, namespaces[i], O_RDONLY));
		check(setns(ns_fd, 0))
		close(ns_fd);
	}

	close(proc_ns_fd);
}

int main(int argc, char **argv)
{
	int cwd_bind_mnt_fd;
	char tmp_dir[] = "/tmp/tmp.XXXXXX";

	if (getpid() == 1) {
		fprintf(stderr, "error: must be run in the host PID namespace\n");
		exit(1);
	}

	if (argc < 2) {
		fprintf(stderr, "usage: %s cmd...\n", argv[0]);
		exit(1);
	}

	check(cwd_bind_mnt_fd = open_tree(AT_FDCWD, "", AT_EMPTY_PATH | OPEN_TREE_CLONE));

	host_nsenter();

	if (mkdtemp(tmp_dir) == NULL) {
		perror("mkdtemp");
		exit(1);
	}

	check(unshare(CLONE_NEWNS));
	check(mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL));

	check(move_mount(cwd_bind_mnt_fd, "", AT_FDCWD, tmp_dir, MOVE_MOUNT_F_EMPTY_PATH));

	check(chdir(tmp_dir));
	check(execv(argv[1], argv + 1));

	return 0;
}
