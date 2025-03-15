# HACK_IT - Math Problem Solver with Visual Animations

## Overview
HACK_IT is a powerful tool that analyzes mathematical problems from images, solves them step-by-step, and generates beautiful Manim animations to visualize the solution process. Perfect for students, educators, and anyone looking to understand mathematical concepts through dynamic visualizations.

## Features
- **Image Analysis**: Upload images containing mathematical problems
- **Smart Problem Detection**: Automatically detects and interprets math problems from images
- **Step-by-Step Solutions**: Provides detailed explanations for each step of the solution
- **Visual Animations**: Generates professional Manim animations to visualize the solution process
- **Educational Tool**: Helps understand complex mathematical concepts through visual learning

## Technology Stack
- Python
- Flask web framework
- LLaVA (Large Language-and-Vision Assistant) for image analysis
- Manim for mathematical animations
- TeX for mathematical typesetting

## Installation

### Prerequisites
- Python 3.8+
- Git

### Setup
1. Clone the repository
```bash
git clone https://github.com/jasonsantoleo/HACK_IT.git
cd HACK_IT
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure the application
```bash
cp config.example.py config.py
# Edit config.py with your API keys and preferences
```

## Usage
1. Start the application
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload an image of a math problem

4. Wait for the analysis and animation generation

5. View the step-by-step solution and accompanying animation

## Project Structure
- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `requirements.txt`: Python dependencies
- `helpers/`: Helper modules
  - `image_helper.py`: Image processing utilities
  - `llm_helper.py`: Language model integration
  - `manim_animator.py`: Animation generation
- `animations/`: Generated animations storage
  - `Tex/`: TeX files for mathematical typesetting
  - `videos/`: Rendered animation videos

## Contributing
We welcome contributions! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- [Manim Community](https://www.manim.community/) for the animation engine
- LLaVA team for the image analysis capabilities
- All participants of the hackathon who provided feedback and support

## Contact
- Jason Santoleo - [GitHub](https://github.com/jasonsantoleo)
