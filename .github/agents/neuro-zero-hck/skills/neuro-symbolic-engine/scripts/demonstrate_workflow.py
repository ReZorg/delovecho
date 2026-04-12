import json
import random

# --- 1. Define the Forms (Data Structures) ---

# form_symbo: A simple symbolic hypergraph
form_symbo = {
    "nodes": [
        {"id": "user_a", "type": "user"},
        {"id": "device_1", "type": "device"},
        {"id": "device_2", "type": "device"},
        {"id": "user_b", "type": "user"},
        {"id": "device_3", "type": "device"}
    ],
    "hyperedges": [
        {"id": "net_corp", "type": "network", "nodes": ["user_a", "device_1", "device_2"]},
        {"id": "net_guest", "type": "network", "nodes": ["user_b", "device_3"]}
    ]
}

# --- 2. Define the Funcs (Operations) ---

def func_manage(initial_state):
    """Simulates retrieving the current symbolic state."""
    print("--- Stage 1: `func_manage` on `form_symbo` ---")
    print("Description: Retrieving the explicit, rule-based state of the symbolic network.")
    num_nodes = len(initial_state['nodes'])
    num_edges = len(initial_state['hyperedges'])
    print(f"Initial symbolic graph has {num_nodes} nodes and {num_edges} hyperedges.")
    return initial_state

def func_embed(symbolic_graph):
    """Simulates the neural embedding process."""
    print("\n--- Stage 2: `func_embed` on `form_symbo` -> `form_meta` ---")
    print("Description: Generating tensor embeddings for each node and hyperedge.")
    
    # Create a deep copy to avoid modifying the original
    meta_graph = json.loads(json.dumps(symbolic_graph))
    
    # Add a random 4-dimensional vector as the embedding
    for node in meta_graph["nodes"]:
        node["embedding"] = [round(random.uniform(-1, 1), 4) for _ in range(4)]
    for hyperedge in meta_graph["hyperedges"]:
        hyperedge["embedding"] = [round(random.uniform(-1, 1), 4) for _ in range(4)]
        
    print("Result: The symbolic graph is now a tensor-attributed hypergraph (`form_meta`).")
    return meta_graph

def func_query(meta_graph, query_node_id="device_1"):
    """Simulates a meta-cognitive query on the attributed hypergraph."""
    print("\n--- Stage 3: `func_query` on `form_meta` ---")
    print(f"Description: Performing a semantic query to find nodes behaviorally similar to [33m{query_node_id}[0m.")
    
    target_embedding = None
    for node in meta_graph["nodes"]:
        if node["id"] == query_node_id:
            target_embedding = node["embedding"]
            break
    
    if not target_embedding:
        print(f"Query node {query_node_id} not found.")
        return []

    print(f"Target embedding for {query_node_id}: {target_embedding}")
    
    similar_nodes = []
    for node in meta_graph["nodes"]:
        if node["id"] == query_node_id:
            continue
        
        # Simple cosine similarity would be used here in a real scenario.
        # For this demo, we simulate similarity with a simple distance measure.
        distance = sum([(a - b) ** 2 for a, b in zip(target_embedding, node["embedding"])]) ** 0.5
        
        if distance < 1.0: # Arbitrary threshold for demonstration
            similar_nodes.append((node["id"], distance))
            
    print("\nResult: Found similar nodes based on embedding proximity.")
    return similar_nodes

# --- 3. Define the Flow (Composition) ---

def flow_pipeline(initial_state):
    """Simulates a multiplicative (⊗) pipeline flow."""
    print("\n=== Executing Neuro-Symbolic Workflow (`⊗` Pipeline) ===")
    
    # skill_get_graph = (func_manage, form_symbo)
    symbolic_state = func_manage(initial_state)
    
    # skill_embed_graph = (func_embed, form_symbo)
    meta_state = func_embed(symbolic_state)
    
    # skill_find_similar = (func_query, form_meta)
    query_results = func_query(meta_state)
    
    print("\n=== Workflow Complete ===")
    print("Final Output:")
    if query_results:
        for node_id, dist in query_results:
            print(f"- Node [32m{node_id}[0m is semantically similar (distance: {dist:.4f})")
    else:
        print("No semantically similar nodes found within the threshold.")

if __name__ == "__main__":
    flow_pipeline(form_symbo)
