import os
import sys
import shutil

def setup_angel(angel_name):
    print(f"🚀 Initializing Echo Angel: {angel_name}")

    base_dir = os.path.join('/home/ubuntu/echo_angels', angel_name)
    if os.path.exists(base_dir):
        print(f"❌ Error: Angel '{angel_name}' already exists at {base_dir}")
        return

    os.makedirs(base_dir)
    print(f"✅ Created angel directory: {base_dir}")

    # Copy core components from unreal-echo
    shutil.copytree('/home/ubuntu/skills/unreal-echo/references', os.path.join(base_dir, 'cognitive_core'))
    print("✅ Copied unreal-echo cognitive core references")

    # Copy expression components from meta-echo-dna
    shutil.copytree('/home/ubuntu/skills/meta-echo-dna/references', os.path.join(base_dir, 'expression_pipeline'))
    print("✅ Copied meta-echo-dna expression pipeline references")

    # Create configuration files
    with open(os.path.join(base_dir, 'config.json'), 'w') as f:
        f.write('{\n')
        f.write('    "angel_name": "' + angel_name + '",\n')
        f.write('    "cognitive_core": {\n')
        f.write('        "reservoir_size": 512,\n')
        f.write('        "spectral_radius": 0.9,\n')
        f.write('        "leak_rate": 0.3\n')
        f.write('    },\n')
        f.write('    "expression_pipeline": {\n')
        f.write('        "chaos_intensity": 0.15,\n')
        f.write('        "confidence_posture": 0.8,\n')
        f.write('        "charisma": 0.7,\n')
        f.write('        "eye_sparkle": 0.9\n')
        f.write('    }\n')
        f.write('}\n')
    print("✅ Created default config.json")

    print(f"\n🎉 Echo Angel '{angel_name}' initialized successfully!")
    print(f"   Location: {base_dir}")
    print("   Next steps:")
    print("   1. Edit config.json to customize your angel's parameters")
    print("   2. Review the copied reference files to understand the architecture")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 setup_angel.py <angel_name>")
    else:
        setup_angel(sys.argv[1])
