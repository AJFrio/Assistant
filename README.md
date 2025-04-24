# Assistant

A modular Python desktop assistant that automates tasks across applications and systems.

## Overview

Assistant is a powerful desktop automation tool with a GUI interface that allows users to:

- Interact with applications (Teams, Outlook, web browsers, etc.)
- Execute system commands
- Check emails and websites
- Send messages and emails
- Delegate tasks to remote computers
- Use AI to intelligently respond to requests

It's built with a modular, maintainable architecture and leverages AI models from OpenAI and Anthropic for natural language understanding.

## Features

- **Natural Language Interface**: Communicate with the assistant using plain English
- **Multi-Application Support**: Control multiple desktop and web applications
- **Task Delegation**: Send tasks to other computers in your network
- **Firebase Integration**: Track task status and manage distributed systems
- **GUI Interface**: Easy-to-use interface with chat-like interaction
- **Voice Mode**: Optional voice input for hands-free operation
- **Extensible Architecture**: Easy to add new functionality

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
assistant/
├── core/           # Core configuration, logging, exceptions
├── api/            # API clients (Firebase, OpenAI, Anthropic)
├── automation/     # System/application/browser automation
├── ui/             # User interface components
├── tasks/          # Task definitions, handlers, processor
├── utils/          # Utility modules
├── main.py         # Application entry point
└── requirements.txt # Dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python libraries (see `requirements.txt`)
- API keys for OpenAI and Firebase (optional: Anthropic)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/assistant.git
   cd assistant
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_API_KEY=your_firebase_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
   ```

### Running the Assistant

Run the main script to start the assistant:

```
python main.py
```

## Configuration

The application loads configuration from environment variables. See the `.env` file example above.

## Adding New Features

The modular architecture makes it easy to add new features:

1. For new task types:
   - Add a task definition in `tasks/types.py`
   - Implement a handler in `tasks/handlers.py`

2. For new automation functionality:
   - Add methods to the appropriate module in `automation/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed by AJ Frio
- Uses OpenAI's GPT models for natural language understanding
- Leverages Firebase for distributed task management
