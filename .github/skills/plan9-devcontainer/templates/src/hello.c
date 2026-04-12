/*
 * Hello — Sample Plan 9 C Program
 * Demonstrates Plan 9 C conventions running inside the devcontainer.
 * Compile: plan9-build compile src/hello.c
 * Run:     plan9-build run src/hello.c
 */

#include <u.h>
#include <libc.h>

void
main(void)
{
	print("╔══════════════════════════════════════════════════════════╗\n");
	print("║  Plan 9 Devcontainer — Hello World                     ║\n");
	print("║  function-creator(inferno-devcontainer)                 ║\n");
	print("╚══════════════════════════════════════════════════════════╝\n");
	print("\n");

	/* Check environment */
	char *plan9 = getenv("PLAN9");
	if(plan9 != nil)
		print("[1] PLAN9 root: %s\n", plan9);
	else
		print("[1] PLAN9 root: not set\n");

	/* Display system info */
	print("[2] Plan 9 C program running successfully.\n");
	print("[3] Use 'plan9-grid start' to launch the CPU server grid.\n");
	print("[4] Use '9 acme' for the native Plan 9 IDE.\n");

	exits(0);
}
