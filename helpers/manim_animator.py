# manim_animator.py
import os
import time
import re
import tempfile
import subprocess
from manim import *

def parse_solution_steps(explanation_text):
    """
    Extract clear mathematical steps from the explanation text.
    Returns a list of dictionaries with equation and explanation parts.
    """
    lines = explanation_text.strip().split('\n')
    steps = []
    current_eq = ""
    current_explanation = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains an equation (has = sign or mathematical symbols)
        if '=' in line or any(symbol in line for symbol in ['+', '-', '×', '÷', '(', ')', '√', '^']):
            # If we already have an equation stored, save it before starting a new one
            if current_eq:
                steps.append({
                    "equation": current_eq,
                    "explanation": current_explanation.strip()
                })
                current_explanation = ""
            
            # Extract the equation part (try to clean any prefixes like "Step 1:" etc.)
            eq_match = re.search(r'(?:Step \d+:?\s*|[•*-]\s*)?(.+)', line)
            if eq_match:
                current_eq = eq_match.group(1).strip()
            else:
                current_eq = line
        else:
            # This line is probably an explanation
            current_explanation += line + " "
    
    # Don't forget to add the last equation
    if current_eq:
        steps.append({
            "equation": current_eq,
            "explanation": current_explanation.strip()
        })
    
    return steps

def generate_manim_script(latex_expression, solution_steps):
    """
    Generate a Manim Python script for animating the solution.
    """
    script = """
from manim import *

class MathSolutionAnimation(Scene):
    def construct(self):
        # Title
        title = Text("Step-by-Step Solution", color=BLUE).scale(0.8)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Original equation
        original_eq = MathTex(r"%s")
        original_eq.next_to(title, DOWN, buff=0.5)
        self.play(Write(original_eq))
        self.wait(1)
        
        # Move original equation to top
        self.play(
            original_eq.animate.scale(0.8).to_corner(UL).shift(DOWN * 0.5 + RIGHT * 0.5)
        )
        self.wait(0.5)
        
        # Create a heading for steps
        steps_title = Text("Solution Steps:", color=YELLOW).scale(0.7)
        steps_title.next_to(title, DOWN, buff=0.5)
        self.play(Write(steps_title))
        self.wait(0.5)
        
        # Track the last equation and explanation for positioning
        last_obj = steps_title
        all_equations = []
        
        # Create and display each step
""" % latex_expression
    
    # Add code for each solution step
    for i, step in enumerate(solution_steps):
        equation = step.get("equation", "").strip()
        explanation = step.get("explanation", "").strip()
        
        # Skip empty steps
        if not equation:
            continue
        
        # Clean the equation for LaTeX
        equation = equation.replace('\\', '\\\\')  # Escape backslashes
        
        # Add the step to the script
        step_script = """
        # Step %d
        step%d_eq = MathTex(r"%s")
        step%d_eq.next_to(last_obj, DOWN, buff=0.5)
        self.play(Write(step%d_eq))
        all_equations.append(step%d_eq)
        last_obj = step%d_eq
        self.wait(1)
        """ % (i+1, i+1, equation, i+1, i+1, i+1, i+1)
        
        script += step_script
        
        # Add explanation if available
        if explanation:
            explanation = explanation.replace('"', '\\"')  # Escape quotes
            explanation_script = """
        # Explanation for step %d
        step%d_exp = Text("%s", color=GRAY).scale(0.5)
        step%d_exp.next_to(step%d_eq, RIGHT, buff=0.5)
        self.play(Write(step%d_exp))
        last_obj = step%d_eq  # Keep positioning relative to equation
        self.wait(1)
            """ % (i+1, i+1, explanation, i+1, i+1, i+1, i+1)
            script += explanation_script
    
    # Add final highlighting for the answer
    script += """
        # Highlight the final answer
        if all_equations:
            final_box = SurroundingRectangle(all_equations[-1], color=GREEN, buff=0.2)
            final_text = Text("Final Answer", color=GREEN).scale(0.7)
            final_text.next_to(final_box, RIGHT, buff=0.5)
            
            self.play(
                Create(final_box),
                Write(final_text)
            )
            self.wait(2)
    """
    
    return script

def create_solution_animation(latex_expression, explanation_text, output_dir="animations", quality="medium"):
    """
    Create a Manim animation from LaTeX expression and explanation text.
    Returns the path to the generated video file.
    """
    # Keep your existing quality_settings for resolution
    quality_settings = {
        "low": {"resolution": "480p"},
        "medium": {"resolution": "720p"},
        "high": {"resolution": "1080p"}
    }
    
    # Add mapping from user-friendly names to Manim's quality flags
    quality_mapping = {
        "low": "l",
        "medium": "m",
        "high": "h"
    }
    
    # Get the corresponding Manim quality flag (default to "m" if not found)
    manim_quality = quality_mapping.get(quality.lower(), "m")
    
    # Use the settings based on quality
    settings = quality_settings.get(quality.lower(), quality_settings["medium"])
    
    # Parse solution steps
    solution_steps = parse_solution_steps(explanation_text)
    
    # Create absolute paths for better reliability
    base_dir = os.path.abspath(os.getcwd())
    output_dir = os.path.join(base_dir, output_dir)
    temp_dir = os.path.join(base_dir, "temp_manim")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create a unique filename for this animation
    timestamp = int(time.time())
    script_filename = os.path.join(temp_dir, f"solution_script_{timestamp}.py")
    output_filename = f"solution_{timestamp}.mp4"
    
    # Generate the Manim script
    script_content = generate_manim_script(latex_expression, solution_steps)
    
    # Write the script to a file
    with open(script_filename, "w") as f:
        f.write(script_content)
    
    try:
        # Run Manim to generate the animation
        print(f"Generating animation with Manim... Quality: {quality} ({manim_quality})")
        
        # Build the command with proper paths
        manim_cmd = [
            "manim", 
            script_filename,
            "MathSolutionAnimation",
            "-o", output_filename,
            "--media_dir", output_dir,
            "-q", manim_quality
        ]
        
        print(f"Running command: {' '.join(manim_cmd)}")
        
        # Use subprocess to run the Manim command with the correct quality flag
        result = subprocess.run(
            manim_cmd, 
            capture_output=True, 
            text=True
        )
        
        # Print full output for debugging
        print(f"Manim stdout: {result.stdout}")
        print(f"Manim stderr: {result.stderr}")
        
        if result.returncode != 0:
            print(f"Manim error (code {result.returncode}): {result.stderr}")
            return None
        
        # Find the path to the generated video (check multiple possible paths)
        possible_paths = [
            os.path.join(output_dir, "videos", "MathSolutionAnimation", output_filename),
            os.path.join(output_dir, "videos", output_filename),
            os.path.join(output_dir, output_filename)
        ]
        
        # Try to find the actual video file
        video_path = None
        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                print(f"Found animation at: {video_path}")
                break
        
        if not video_path:
            # List contents of output directory to help debug
            print("Animation file not found. Contents of output directories:")
            for root, dirs, files in os.walk(output_dir):
                print(f"Directory: {root}")
                for file in files:
                    if file.endswith(".mp4"):
                        found_path = os.path.join(root, file)
                        print(f"Found MP4: {found_path}")
                        # Use the first mp4 found if we can't find the exact file
                        if not video_path and "solution" in file:
                            video_path = found_path
            
            if not video_path:
                print("No animation files found after generation.")
                return None
        
        return video_path
    except Exception as e:
        print(f"Error generating animation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up the script file
        if os.path.exists(script_filename):
            os.remove(script_filename)

# Example usage
if __name__ == "__main__":
    # Sample data for testing
    latex_equation = "2x + 5 = 15"
    explanation = """
    Step 1: 2x + 5 = 15
    First, we subtract 5 from both sides.
    
    Step 2: 2x = 10
    Now we divide both sides by 2.
    
    Step 3: x = 5
    This is our final answer.
    """
    
    video_path = create_solution_animation(latex_equation, explanation)
    if video_path:
        print(f"Animation created successfully at: {video_path}")
    else:
        print("Failed to create animation.")