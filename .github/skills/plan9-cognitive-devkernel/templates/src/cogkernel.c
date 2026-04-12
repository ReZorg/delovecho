/*
 * Cognitive Kernel Demo — Plan 9 C
 *
 * Demonstrates the OpenCog-Plan9 cognitive kernel services
 * running on Plan 9 from Bell Labs.
 *
 * Compile: 6c cogkernel.c && 6l -o cogkernel cogkernel.6
 * Run:     ./cogkernel
 */

#include <u.h>
#include <libc.h>

/* Truth value for atoms */
typedef struct TruthValue TruthValue;
struct TruthValue {
	double strength;
	double confidence;
};

/* Print a truth value */
void
tvprint(TruthValue tv)
{
	print("<%.2f, %.2f>", tv.strength, tv.confidence);
}

/* Check if a cognitive namespace path is mounted */
int
nsmounted(char *path)
{
	Dir *d;

	d = dirstat(path);
	if(d == nil)
		return 0;
	free(d);
	return 1;
}

void
main(int, char**)
{
	TruthValue tv;
	char *services[] = {
		"/cognitive/atomspace",
		"/cognitive/inference",
		"/cognitive/attention",
		"/cognitive/learning",
	};
	int i;

	print("+========================================================+\n");
	print("|  OpenCog-Plan9 Cognitive Kernel Demo                    |\n");
	print("|  Running on Plan 9 from Bell Labs                      |\n");
	print("+========================================================+\n");
	print("\n");

	/* Demonstrate AtomSpace operations */
	print("[1] Creating atoms in local AtomSpace...\n");
	tv = (TruthValue){1.0, 0.9};
	print("    ConceptNode 'cat' ");
	tvprint(tv);
	print("\n");
	print("    ConceptNode 'animal' ");
	tvprint(tv);
	print("\n");
	tv = (TruthValue){0.95, 0.85};
	print("    InheritanceLink (cat, animal) ");
	tvprint(tv);
	print("\n");

	/* Check network stack */
	print("\n[2] Checking network stack...\n");
	if(nsmounted("/net/tcp"))
		print("    + Network stack available (/net/tcp)\n");
	else
		print("    X Network stack not bound (run: bind '#I' /net)\n");

	/* Check factotum */
	print("\n[3] Checking authentication...\n");
	if(nsmounted("/mnt/factotum"))
		print("    + factotum available\n");
	else
		print("    X factotum not running\n");

	/* Check cognitive services */
	print("\n[4] Cognitive services status:\n");
	for(i = 0; i < nelem(services); i++){
		if(nsmounted(services[i]))
			print("    + %s -- active\n", services[i]);
		else
			print("    o %s -- not mounted\n", services[i]);
	}

	print("\n[5] Cognitive kernel demo complete.\n");
	print("    Use 'plan9-grid start' to launch distributed CPU servers.\n");

	exits(nil);
}
