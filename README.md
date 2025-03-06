# AI-Driven Browser Automation Agent

An autonomous browser agent that can perform complex web tasks based on natural language instructions. The agent uses computer vision, OCR, and AI reasoning to understand web pages and navigate them intelligently.

## Features

- 🤖 Autonomous navigation and interaction with websites
- 👁️ Vision-based understanding of web pages using YOLOv8
- 📝 Text extraction with OCR
- 🧠 Intelligent decision-making using DeepSeek AI
- 🔄 Continuous feedback loop for adaptive behavior
- 🔍 Flexible search detection across different websites
- 🍪 Smart cookie banner handling

## Requirements

- Python 3.8+
- Chrome browser installed

## Setup

1. Install dependencies:
pip install -r requirements.txt
playwright install
Copy
2. Create a `.env` file with your API keys:
GROQ_API_KEY=your_groq_api_key
CHROME_PROFILE_PATH=C:\path\to\your\chrome\profile
Copy
## Usage

Run the agent with:
python -m src.main
Copy
When prompted, enter your desired task in natural language, such as:
- "Search for iPhone 16 Pro on Amazon"
- "Find a good recipe for chocolate cake"
- "Look up the weather forecast for New York"

## How It Works

1. **Vision Processing**: Uses YOLOv8 and OCR to understand what's on the screen
2. **AI Reasoning**: DeepSeek AI interprets the visual data and decides what actions to take
3. **Browser Automation**: Playwright executes the AI's commands with human-like behavior
4. **Feedback Loop**: The agent continuously monitors results and adjusts its approach
5. **Flexible Search**: Intelligently detects and interacts with search interfaces across different websites