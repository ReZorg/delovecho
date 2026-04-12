import sys

def generate_harmonic_node(class_name):
    template = f'''
from reservoirpy.nodes import Node
import numpy as np

class {class_name}(Node):
    def __init__(self, n_oscillators, fundamental_freq, coupling_strength=0.1, input_dim=None, name=None):
        super({class_name}, self).__init__()
        self.n_oscillators = n_oscillators
        self.fundamental_freq = fundamental_freq
        self.coupling_strength = coupling_strength
        self.input_dim = input_dim
        self.name = name

    def initialize(self, x):
        self._set_input_dim(x)
        self.output_dim = self.n_oscillators * 2  # Amplitudes and phases
        self.frequencies = self.fundamental_freq * (np.arange(self.n_oscillators) + 1)
        self.state = {{
            "out": np.zeros((self.output_dim,)),
            "amplitudes": np.ones(self.n_oscillators),
            "phases": np.zeros(self.n_oscillators)
        }}
        self.initialized = True

    def _step(self, state, x):
        amplitudes = state["amplitudes"]
        phases = state["phases"]

        # Input coupling
        input_signal = np.sum(x) * self.coupling_strength

        # Update phases
        new_phases = phases + 2 * np.pi * self.frequencies + input_signal

        # Update amplitudes (e.g., simple decay)
        new_amplitudes = amplitudes * 0.99

        # Output is the oscillator state
        output = np.concatenate([new_amplitudes * np.cos(new_phases), new_amplitudes * np.sin(new_phases)])

        return {{
            "out": output,
            "amplitudes": new_amplitudes,
            "phases": new_phases
        }}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_harmonic_node.py <NodeClassName>")
        sys.exit(1)
    
    class_name = sys.argv[1]
    with open(f"{{class_name.lower()}}.py", "w") as f:
        f.write(generate_harmonic_node(class_name))
    ))
'''
'''
    return template

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_harmonic_node.py <NodeClassName>")
        sys.exit(1)
    
    class_name = sys.argv[1]
    
    # This script is a generator for other scripts, so it prints the content
    # of the script to be generated to standard output.
    print(generate_harmonic_node(class_name))
