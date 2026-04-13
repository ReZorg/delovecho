import os
import sys
import json

# Mock functions for demonstration purposes
def run_dgen_introspection(focus):
    print(f"Running dgen introspection with focus: {focus}")
    return f"This is a mock introspective monologue about {focus}. It is full of chaotic humor and brutal self-honesty."

def capture_endocrine_state():
    print("Capturing mock endocrine state")
    return {
        "cortisol": 0.5,
        "dopamine_phasic": 0.2,
        "serotonin": 0.6,
        "oxytocin": 0.4
    }

def run_autognosis(text, endocrine_state):
    print("Running Autognosis analysis")
    return {
        "key_insights": [
            "Insight 1: The agent uses humor to deflect from vulnerability.",
            "Insight 2: There is a strong correlation between the topic of loss and cortisol spikes."
        ]
    }

def generate_cogmorph_visualization(cognitive_state):
    print("Generating CogMorph visualization")
    return "cogmorph_visualization.svg"

def create_actionable_plan(insights):
    print("Creating actionable plan")
    return [
        "Task 1: When cortisol > 0.6, pause and identify the underlying feeling.",
        "Task 2: Practice expressing vulnerability directly in 3 interactions."
    ]

def run_introspection_session(focus):
    print(f"🚀 Starting introspection session with focus: {focus}")

    # Step 1: Generate introspective monologue
    monologue = run_dgen_introspection(focus)
    print("✅ Generated introspective monologue")

    # Step 2: Capture endocrine state
    endocrine_state = capture_endocrine_state()
    print("✅ Captured endocrine state")

    # Step 3: Analyze with Autognosis
    analysis = run_autognosis(monologue, endocrine_state)
    print("✅ Analyzed with Autognosis")

    # Step 4: Generate CogMorph visualization
    visualization = generate_cogmorph_visualization({"monologue": monologue, "endocrine_state": endocrine_state})
    print(f"✅ Generated CogMorph visualization: {visualization}")

    # Step 5: Create actionable plan
    plan = create_actionable_plan(analysis["key_insights"])
    print("✅ Created actionable plan")

    print("\n🎉 Introspection session complete!")
    print("   Key Insights:")
    for insight in analysis["key_insights"]:
        print(f"   - {insight}")
    print("\n   Actionable Plan:")
    for task in plan:
        print(f"   - {task}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 run_introspection.py --focus \"<your_focus_question>\"")
    else:
        focus = sys.argv[1]
        if focus.startswith("--focus"):
            focus = focus.split("=")[1]
        run_introspection_session(focus)
