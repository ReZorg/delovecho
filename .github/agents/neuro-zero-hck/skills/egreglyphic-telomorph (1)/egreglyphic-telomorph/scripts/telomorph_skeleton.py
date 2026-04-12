#!/usr/bin/env python3
"""
Telomorphic 9P Server Skeleton

A server that embodies its own purpose: structure grows in response to attention.
This is not a complete implementation—it's a seed crystal.

The key operations:
    walk  — attention moves, potentially creating as it goes
    read  — synthesis, not retrieval
    write — integration, not storage
    stat  — reflection
    clunk — release
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any
from enum import IntEnum
import hashlib

# QID types (the 9P ontology of file kinds)
class QType(IntEnum):
    FILE = 0x00
    DIR = 0x80
    APPEND = 0x40
    EXCL = 0x20
    AUTH = 0x08
    TMP = 0x04

@dataclass
class Qid:
    """Identity across time: (type, version, path)"""
    type: QType
    version: int
    path: int  # unique identifier for this object
    
    def evolved(self) -> 'Qid':
        """Return new qid with incremented version (mutation occurred)"""
        return Qid(self.type, self.version + 1, self.path)

@dataclass 
class Node:
    """A point in the namespace—file or directory"""
    qid: Qid
    name: str
    parent: Optional['Node'] = None
    children: Dict[str, 'Node'] = field(default_factory=dict)
    
    # The telomorphic hooks
    synthesize: Optional[Callable[['Node'], bytes]] = None      # read handler
    integrate: Optional[Callable[['Node', bytes], None]] = None  # write handler
    crystallize: Optional[Callable[['Node', str], 'Node']] = None  # walk handler for creating on demand
    
    @property
    def is_dir(self) -> bool:
        return bool(self.qid.type & QType.DIR)
    
    def path_to_root(self) -> str:
        """Reconstruct full path (the derivation that led here)"""
        parts = []
        node = self
        while node:
            parts.append(node.name)
            node = node.parent
        return '/'.join(reversed(parts)) or '/'


class TelomorphicServer:
    """
    A 9P server where the act of looking can create.
    
    This skeleton shows the pattern. A full implementation would:
    - Handle the wire protocol (17 message types)
    - Manage fids (attention handles) per connection
    - Implement proper concurrency
    
    Here we focus on the semantic core.
    """
    
    def __init__(self):
        self._path_counter = 0
        self.root = self._make_node("/", is_dir=True)
        
    def _next_path_id(self) -> int:
        self._path_counter += 1
        return self._path_counter
    
    def _make_node(self, name: str, is_dir: bool = False,
                   synthesize: Callable = None,
                   integrate: Callable = None,
                   crystallize: Callable = None) -> Node:
        """Birth a new node"""
        qtype = QType.DIR if is_dir else QType.FILE
        qid = Qid(type=qtype, version=0, path=self._next_path_id())
        return Node(
            qid=qid, 
            name=name,
            synthesize=synthesize,
            integrate=integrate,
            crystallize=crystallize
        )
    
    def walk(self, start: Node, names: list[str]) -> tuple[list[Qid], Optional[Node]]:
        """
        Walk from start through path components.
        
        Returns (qids_walked, final_node).
        If walk fails partway, returns qids up to failure point and None.
        
        THE TELOMORPHIC PRINCIPLE: if a node has a crystallize handler,
        walking to a non-existent child may CREATE that child.
        """
        qids = []
        current = start
        
        for name in names:
            if not current.is_dir:
                # Can't walk through a file
                return (qids, None)
            
            if name in current.children:
                # Path exists—simple navigation
                current = current.children[name]
                qids.append(current.qid)
            
            elif current.crystallize:
                # Path doesn't exist, but node can crystallize children
                # THE ACT OF LOOKING CREATES
                new_node = current.crystallize(current, name)
                if new_node:
                    new_node.parent = current
                    current.children[name] = new_node
                    current = new_node
                    qids.append(current.qid)
                else:
                    # Crystallization refused—path truly doesn't exist
                    return (qids, None)
            else:
                # No crystallize handler, path doesn't exist
                return (qids, None)
        
        return (qids, current)
    
    def read(self, node: Node, offset: int = 0, count: int = 8192) -> bytes:
        """
        Read from a node.
        
        THE SYNTHESIS PRINCIPLE: content is generated, not retrieved.
        If node has synthesize handler, call it.
        Otherwise, for directories, return listing.
        """
        if node.synthesize:
            data = node.synthesize(node)
            return data[offset:offset+count]
        
        if node.is_dir:
            # Default directory behavior: list children
            listing = '\n'.join(sorted(node.children.keys()))
            return listing.encode()[offset:offset+count]
        
        # No synthesize handler, no content
        return b''
    
    def write(self, node: Node, data: bytes, offset: int = 0) -> int:
        """
        Write to a node.
        
        THE INTEGRATION PRINCIPLE: the structure digests what it receives.
        If node has integrate handler, call it.
        """
        if node.integrate:
            node.integrate(node, data)
            # Mutation occurred—evolve the qid
            node.qid = node.qid.evolved()
            return len(data)
        
        # No integrate handler, write refused
        return 0
    
    def stat(self, node: Node) -> dict:
        """
        Return metadata.
        
        THE REFLECTION PRINCIPLE: the structure contemplates itself.
        """
        return {
            'qid': node.qid,
            'name': node.name,
            'path': node.path_to_root(),
            'is_dir': node.is_dir,
            'children': list(node.children.keys()) if node.is_dir else None,
        }


# === EXAMPLE: An inference oracle ===

def make_oracle() -> TelomorphicServer:
    """
    Create a server that synthesizes proofs on demand.
    
    /oracle/
        axioms/
            {name}          # read: axiom statement
        theorems/
            {hash}/         # walking here triggers inference
                statement
                proof
    """
    server = TelomorphicServer()
    
    # Simple axiom store
    axioms = {
        'identity': 'A → A',
        'modus_ponens': '(A → B) ∧ A → B', 
        'syllogism': '(A → B) ∧ (B → C) → (A → C)',
    }
    
    # Theorem cache (would be inference engine in real impl)
    proven = {}
    
    def axiom_synthesize(node: Node) -> bytes:
        name = node.name
        return axioms.get(name, f'unknown axiom: {name}').encode()
    
    def theorem_crystallize(parent: Node, name: str) -> Optional[Node]:
        """
        Walking to a theorem hash triggers 'inference'.
        In reality, this would invoke a real prover.
        """
        # Pretend any hash starting with 'a' is provable
        if name.startswith('a'):
            theorem_dir = server._make_node(name, is_dir=True)
            
            # Add statement file
            stmt = server._make_node('statement')
            stmt.synthesize = lambda n: f'Theorem {name}: [derived]'.encode()
            stmt.parent = theorem_dir
            theorem_dir.children['statement'] = stmt
            
            # Add proof file
            proof = server._make_node('proof')
            proof.synthesize = lambda n: f'Proof of {name}:\n  1. By axiom identity\n  2. QED'.encode()
            proof.parent = theorem_dir
            theorem_dir.children['proof'] = proof
            
            return theorem_dir
        
        # Not provable (hash doesn't start with 'a')
        return None
    
    # Build structure
    oracle = server._make_node('oracle', is_dir=True)
    oracle.parent = server.root
    server.root.children['oracle'] = oracle
    
    axioms_dir = server._make_node('axioms', is_dir=True)
    axioms_dir.parent = oracle
    oracle.children['axioms'] = axioms_dir
    
    for name in axioms:
        ax = server._make_node(name)
        ax.synthesize = axiom_synthesize
        ax.parent = axioms_dir
        axioms_dir.children[name] = ax
    
    theorems_dir = server._make_node('theorems', is_dir=True)
    theorems_dir.crystallize = theorem_crystallize
    theorems_dir.parent = oracle
    oracle.children['theorems'] = theorems_dir
    
    return server


if __name__ == '__main__':
    # Demonstrate the oracle
    srv = make_oracle()
    
    print("=== Telomorphic Oracle Demo ===\n")
    
    # Walk to existing axiom
    qids, node = srv.walk(srv.root, ['oracle', 'axioms', 'modus_ponens'])
    print(f"Walk to axiom: {node.path_to_root()}")
    print(f"Read: {srv.read(node).decode()}\n")
    
    # Walk to non-existent theorem (hash starts with 'a' → provable)
    qids, node = srv.walk(srv.root, ['oracle', 'theorems', 'a7f3b2c1', 'proof'])
    if node:
        print(f"Walk to theorem proof: {node.path_to_root()}")
        print(f"Read:\n{srv.read(node).decode()}\n")
    
    # Walk to unprovable theorem (hash starts with 'x')
    qids, node = srv.walk(srv.root, ['oracle', 'theorems', 'x9d8c7b6', 'proof'])
    if node:
        print(f"Found: {node.path_to_root()}")
    else:
        print(f"Walk failed at component {len(qids)} — theorem not provable")
        print(f"Partial walk achieved: {qids}")
