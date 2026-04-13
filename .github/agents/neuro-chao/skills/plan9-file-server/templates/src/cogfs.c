/*
 * Cognitive File Server (cogfs) — Plan 9 C
 *
 * A 9P2000 file server that exposes the full /cognitive/ namespace.
 * Designed to run on the file server node and be mounted by CPU servers.
 *
 * Namespace:
 *   /cognitive/atomspace/{atoms,types,indices}
 *   /cognitive/inference/{rules,queue,results}
 *   /cognitive/attention/{bank,agents}
 *   /cognitive/learning/{populations,fitness}
 *   /cognitive/temporal/{levels,phases}
 *   /cognitive/autognosis/{images,insights,metrics}
 *
 * Compile: 6c cogfs.c && 6l -o cogfs cogfs.6
 * Run:     ./cogfs [-p port] [-m mountpoint]
 */

#include <u.h>
#include <libc.h>
#include <fcall.h>
#include <thread.h>
#include <9p.h>

/* Cognitive service directories */
typedef struct CogDir CogDir;
struct CogDir {
	char *path;
	char *desc;
	int   perm;
};

CogDir cogdirs[] = {
	{ "atomspace",             "AtomSpace root",                  DMDIR|0775 },
	{ "atomspace/atoms",       "Atom instances",                  DMDIR|0775 },
	{ "atomspace/types",       "Type hierarchy",                  DMDIR|0555 },
	{ "atomspace/indices",     "Lookup indices",                  DMDIR|0555 },
	{ "inference",             "PLN inference engine",             DMDIR|0775 },
	{ "inference/rules",       "Inference rules",                 DMDIR|0555 },
	{ "inference/queue",       "Pending tasks",                   DMDIR|0775 },
	{ "inference/results",     "Cached results",                  DMDIR|0555 },
	{ "attention",             "ECAN attention allocation",       DMDIR|0775 },
	{ "attention/bank",        "STI/LTI values",                  DMDIR|0775 },
	{ "attention/agents",      "Attention agents",                DMDIR|0555 },
	{ "learning",              "MOSES learning",                  DMDIR|0775 },
	{ "learning/populations",  "Candidate populations",           DMDIR|0775 },
	{ "learning/fitness",      "Fitness evaluators",              DMDIR|0555 },
	{ "temporal",              "Time crystal hierarchy",          DMDIR|0555 },
	{ "temporal/levels",       "Hierarchy level configs",         DMDIR|0555 },
	{ "temporal/phases",       "Phase state per level",           DMDIR|0555 },
	{ "autognosis",            "Self-monitoring",                 DMDIR|0555 },
	{ "autognosis/images",     "Hierarchical self-images",        DMDIR|0555 },
	{ "autognosis/insights",   "Meta-cognitive insights",         DMDIR|0555 },
	{ "autognosis/metrics",    "Self-monitoring metrics",         DMDIR|0555 },
};

/* Status file content */
char *statustext =
	"cogfs — Plan 9 Cognitive File Server\n"
	"Composition: plan9-cognitive-devkernel[file-server]\n"
	"Status: running\n";

void
fsread(Req *r)
{
	if(strcmp(r->fid->file->name, "status") == 0){
		readstr(r, statustext);
		respond(r, nil);
		return;
	}
	respond(r, "not implemented");
}

void
fswrite(Req *r)
{
	/* ctl commands: mount, unmount, sync, snapshot */
	if(strcmp(r->fid->file->name, "ctl") == 0){
		r->ofcall.count = r->ifcall.count;
		respond(r, nil);
		return;
	}
	respond(r, "permission denied");
}

Srv fs = {
	.read  = fsread,
	.write = fswrite,
};

File*
findorcreate(File *root, char *path, int perm)
{
	char buf[256], *parts[16];
	int n, i;
	File *f;

	strncpy(buf, path, sizeof(buf)-1);
	buf[sizeof(buf)-1] = 0;

	n = tokenize(buf, parts, nelem(parts));
	f = root;
	for(i = 0; i < n; i++){
		File *child = nil;
		/* Walk to find existing child */
		/* If not found, create it */
		child = createfile(f, parts[i], nil, perm, nil);
		if(child == nil){
			/* Already exists, walk to it */
			/* In production, use walkfile */
			return nil;
		}
		f = child;
	}
	return f;
}

void
usage(void)
{
	fprint(2, "usage: cogfs [-p port] [-m mountpoint]\n");
	exits("usage");
}

void
main(int argc, char **argv)
{
	char *port = "5640";
	char *mtpt = "/cognitive";
	Tree *tree;
	File *root;
	int i;

	ARGBEGIN{
	case 'p':
		port = EARGF(usage());
		break;
	case 'm':
		mtpt = EARGF(usage());
		break;
	default:
		usage();
	}ARGEND

	tree = alloctree(nil, nil, DMDIR|0555, nil);
	root = tree->root;

	/* Create cognitive namespace directories */
	for(i = 0; i < nelem(cogdirs); i++)
		findorcreate(root, cogdirs[i].path, cogdirs[i].perm);

	/* Control and status files */
	createfile(root, "ctl", nil, 0666, nil);
	createfile(root, "status", nil, 0444, nil);

	fs.tree = tree;

	print("Cognitive File Server starting\n");
	print("  Port: %s\n", port);
	print("  Mount: %s\n", mtpt);
	print("  Namespace: %d directories\n", nelem(cogdirs));
	print("\n");
	print("Remote mount:\n");
	print("  srv tcp!<host>!%s cogfs\n", port);
	print("  mount /srv/cogfs %s\n", mtpt);

	postmountsrv(&fs, "cogfs", mtpt, MREPL);
	exits(nil);
}
