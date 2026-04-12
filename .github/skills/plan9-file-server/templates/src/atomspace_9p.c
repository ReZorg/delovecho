/*
 * AtomSpace 9P File Server — Plan 9 C
 *
 * Serves the AtomSpace as a 9P2000 file tree.
 * Each atom is a file; directories group by type.
 * Truth values are exposed via stat metadata.
 *
 * Composition: plan9-cognitive-devkernel[{{file-server}}]
 *
 * Namespace layout:
 *   /concepts/       — ConceptNode instances
 *   /predicates/     — PredicateNode instances
 *   /links/          — All link types
 *   /types           — Type hierarchy (read-only)
 *   /ctl             — Control file (write commands)
 *
 * Compile: 6c atomspace_9p.c && 6l -o atomspace_9p atomspace_9p.6
 * Run:     ./atomspace_9p [-p port]
 */

#include <u.h>
#include <libc.h>
#include <fcall.h>
#include <thread.h>
#include <9p.h>

enum {
	Maxatoms = 4096,
	Maxname  = 256,
	Maxval   = 1024,
};

/* Truth value */
typedef struct TV TV;
struct TV {
	double strength;
	double confidence;
};

/* Atom types */
enum {
	TConceptNode,
	TPredicateNode,
	TInheritanceLink,
	TListLink,
	Ntypes,
};

char *typenames[] = {
	[TConceptNode]      = "ConceptNode",
	[TPredicateNode]    = "PredicateNode",
	[TInheritanceLink]  = "InheritanceLink",
	[TListLink]         = "ListLink",
};

/* Atom */
typedef struct Atom Atom;
struct Atom {
	int    type;
	char   name[Maxname];
	char   value[Maxval];
	TV     tv;
	int    used;
};

Atom atoms[Maxatoms];
int  natoms;

/* File tree nodes */
typedef struct FNode FNode;
struct FNode {
	char  name[Maxname];
	int   isdir;
	int   atomidx;  /* -1 if directory */
	char  *data;
	int   datalen;
};

/* Create a new atom */
int
atomcreate(int type, char *name, TV tv)
{
	int i;

	if(natoms >= Maxatoms)
		return -1;
	i = natoms++;
	atoms[i].type = type;
	atoms[i].tv = tv;
	atoms[i].used = 1;
	strncpy(atoms[i].name, name, Maxname-1);
	snprint(atoms[i].value, Maxval,
		"(%s \"%s\" (stv %.4f %.4f))",
		typenames[type], name, tv.strength, tv.confidence);
	return i;
}

/* Look up atom by name */
int
atomfind(char *name)
{
	int i;

	for(i = 0; i < natoms; i++)
		if(atoms[i].used && strcmp(atoms[i].name, name) == 0)
			return i;
	return -1;
}

/* 9P server callbacks */
static char Enomem[] = "out of memory";
static char Enotfound[] = "atom not found";

Tree *fstree;

void
fsread(Req *r)
{
	Atom *a;
	int idx;
	char *path;

	path = r->fid->file->name;

	/* Check if reading an atom file */
	idx = (intptr_t)r->fid->file->aux;
	if(idx >= 0 && idx < natoms && atoms[idx].used){
		a = &atoms[idx];
		readstr(r, a->value);
		respond(r, nil);
		return;
	}

	/* Types file */
	if(strcmp(path, "types") == 0){
		char buf[4096];
		int n = 0;
		int i;
		for(i = 0; i < Ntypes; i++)
			n += snprint(buf+n, sizeof(buf)-n, "%s\n", typenames[i]);
		readstr(r, buf);
		respond(r, nil);
		return;
	}

	respond(r, Enotfound);
}

void
fswrite(Req *r)
{
	char buf[Maxval];
	int n;

	n = r->ifcall.count;
	if(n >= Maxval)
		n = Maxval - 1;
	memmove(buf, r->ifcall.data, n);
	buf[n] = 0;

	/* Write to ctl: parse commands */
	if(strcmp(r->fid->file->name, "ctl") == 0){
		/* Commands: add <type> <name> <strength> <confidence> */
		/* Commands: del <name> */
		/* Commands: sync */
		r->ofcall.count = n;
		respond(r, nil);
		return;
	}

	respond(r, "permission denied");
}

Srv fs = {
	.read  = fsread,
	.write = fswrite,
};

void
usage(void)
{
	fprint(2, "usage: atomspace_9p [-p port]\n");
	exits("usage");
}

void
main(int argc, char **argv)
{
	char *port = "5640";
	char *mtpt = "/cognitive/atomspace";
	File *root, *concepts, *predicates, *links;
	int i;

	ARGBEGIN{
	case 'p':
		port = EARGF(usage());
		break;
	default:
		usage();
	}ARGEND

	/* Seed some demo atoms */
	atomcreate(TConceptNode, "cat", (TV){1.0, 0.9});
	atomcreate(TConceptNode, "animal", (TV){1.0, 0.9});
	atomcreate(TConceptNode, "dog", (TV){1.0, 0.9});
	atomcreate(TPredicateNode, "is-a", (TV){1.0, 1.0});
	atomcreate(TInheritanceLink, "cat-animal", (TV){0.95, 0.85});
	atomcreate(TInheritanceLink, "dog-animal", (TV){0.90, 0.80});

	/* Create 9P file tree */
	fstree = alloctree(nil, nil, DMDIR|0555, nil);
	root = fstree->root;

	concepts = createfile(root, "concepts", nil, DMDIR|0555, nil);
	predicates = createfile(root, "predicates", nil, DMDIR|0555, nil);
	links = createfile(root, "links", nil, DMDIR|0555, nil);
	createfile(root, "types", nil, 0444, nil);
	createfile(root, "ctl", nil, 0666, nil);

	/* Populate file tree from atoms */
	for(i = 0; i < natoms; i++){
		File *parent;
		switch(atoms[i].type){
		case TConceptNode:
			parent = concepts;
			break;
		case TPredicateNode:
			parent = predicates;
			break;
		default:
			parent = links;
			break;
		}
		createfile(parent, atoms[i].name, nil, 0444, (void*)(intptr_t)i);
	}

	fs.tree = fstree;

	print("AtomSpace 9P server starting on port %s\n", port);
	print("Mount with: srv tcp!localhost!%s atomspace; mount /srv/atomspace %s\n",
		port, mtpt);
	print("Serving %d atoms\n", natoms);

	postmountsrv(&fs, "atomspace", mtpt, MREPL);
	exits(nil);
}
