#!/usr/bin/env python3
"""
CogSim Setup Script

Clones and sets up the CogSim framework for process-centric simulation.
Run this before creating simulations.
"""

import subprocess
import sys
import os


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)


def setup_cogsim(target_dir: str = "/home/ubuntu/cogsim") -> bool:
    """
    Set up CogSim framework.
    
    Args:
        target_dir: Directory to clone CogSim into
        
    Returns:
        True if successful, False otherwise
    """
    print("Setting up CogSim...")
    
    # Check if already exists
    if os.path.exists(os.path.join(target_dir, "cogsim", "__init__.py")):
        print(f"✓ CogSim already installed at {target_dir}")
        return True
    
    # Clone repository
    if os.path.exists(target_dir):
        print(f"  Removing existing directory: {target_dir}")
        run_command(f"rm -rf {target_dir}", check=False)
    
    print("  Cloning cogpy/cogsim...")
    result = run_command(f"gh repo clone cogpy/cogsim {target_dir}", check=False)
    
    if result.returncode != 0:
        print(f"✗ Failed to clone: {result.stderr}")
        return False
    
    # Verify installation
    verify_script = f"""
import sys
sys.path.insert(0, '{target_dir}')
from cogsim import SimulationEngine, Source, Sink
print("CogSim imported successfully")
"""
    
    result = run_command(f'python3 -c "{verify_script}"', check=False)
    
    if result.returncode == 0:
        print(f"✓ CogSim installed and verified at {target_dir}")
        return True
    else:
        print(f"✗ Verification failed: {result.stderr}")
        return False


def print_quick_start():
    """Print quick start guide."""
    print("""
CogSim Quick Start
==================

1. Import CogSim:
   import sys
   sys.path.insert(0, '/home/ubuntu/cogsim')
   from cogsim import SimulationEngine, Source, Sink, Service, ArrivalMode, RandomVariate

2. Create simulation:
   engine = SimulationEngine(seed=42)
   rv = RandomVariate(seed=42)
   
   source = Source("arrivals", arrival_mode=ArrivalMode.RATE, rate=1.0, engine=engine)
   service = Service("server", service_time=lambda: rv.exponential(0.8), engine=engine)
   sink = Sink("exit", engine=engine)
   
   source >> service >> sink
   engine.run(until=1000)
   
   print(sink.get_statistics())

3. See examples:
   /home/ubuntu/cogsim/examples/bank_teller.py
   /home/ubuntu/cogsim/examples/manufacturing_line.py
   /home/ubuntu/cogsim/examples/skincare_salon.py
   /home/ubuntu/cogsim/examples/skincare_production_plant.py
""")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/cogsim"
    
    if setup_cogsim(target):
        print_quick_start()
    else:
        sys.exit(1)
