// Executable inside each automation's app, compiled by install.sh with -DINTERPRETER,
// -DSCRIPT and -DACCESS_DIR (relative to $HOME). It runs the script bundled in the app's
// Resources as a child process (never exec), so macOS charges the script's file access to
// the app, and the app only needs permission for its own folder.
//
// Usage: <app>/Contents/MacOS/<name> [--check-access | script args...]
//   --check-access  open ACCESS_DIR so macOS asks for permission now, then report and exit

#include <dirent.h>
#include <errno.h>
#include <libgen.h>
#include <limits.h>
#include <mach-o/dyld.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>

extern char **environ;

static int check_access(void) {
    char dir[PATH_MAX];
    snprintf(dir, sizeof dir, "%s/%s", getenv("HOME"), ACCESS_DIR);
    DIR *d = opendir(dir);
    if (!d || (errno = 0, readdir(d) == NULL && errno)) {
        printf("No access to %s: %s\n", dir, strerror(errno));
        return 1;
    }
    closedir(d);
    printf("Access to %s OK\n", dir);
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--check-access") == 0)
        return check_access();

    // <app>/Contents/MacOS/<name> -> <app>/Contents/Resources/SCRIPT
    char exe[PATH_MAX], real[PATH_MAX], script[PATH_MAX];
    uint32_t size = sizeof exe;
    if (_NSGetExecutablePath(exe, &size) != 0 || !realpath(exe, real)) {
        fprintf(stderr, "Can't find own path\n");
        return 1;
    }
    snprintf(script, sizeof script, "%s/../Resources/%s", dirname(real), SCRIPT);

    char **args = calloc(argc + 2, sizeof *args);
    args[0] = INTERPRETER;
    args[1] = script;
    for (int i = 1; i < argc; i++)
        args[i + 1] = argv[i];

    pid_t pid;
    int err = posix_spawn(&pid, INTERPRETER, NULL, NULL, args, environ);
    if (err) {
        fprintf(stderr, "Can't run %s: %s\n", INTERPRETER, strerror(err));
        return 1;
    }
    int status;
    while (waitpid(pid, &status, 0) < 0 && errno == EINTR)
        ;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
