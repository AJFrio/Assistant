# CAS-E

This project is a virtual assistant (Central Automated System, CAS-E) application designed to use your computer. It includes functionalities such as sending messages, opening applications, reading emails, and more.

## Features

- **Send Messages**: Send messages using Teams (`send_message`).
- **Open Applications**: Open specified applications on your computer (`open_app`).
- **Check Email**: Read and summarize the most recent emails from Outlook (`check_email`).
- **Send Email**: Send emails via Outlook (`send_email`).
- **Get System Information**: Retrieve current date/time and system/connection information (`get_info`).
- **Check Website**: Request info/summaries from websites by providing a URL and context (`check_website`).
- **Check Jira**: Check for recent Jira tickets assigned to you (requires `JIRA_URL` in `.env`) (`check_jira`).
- **Interact with Cursor**: Send prompts to the Cursor IDE (`use_cursor`).
- **Run PowerShell Command**: Execute a specified command in a PowerShell window (`run_command`).
- **Learn Function**: *[Experimental]* Attempts to learn a new function based on a command (`learn_function`).

## Setup

### Prerequisites

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AJFrio/Assistant
   ```

2. Navigate to the project directory:
   ```bash
   cd Assistant
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your API keys and other necessary environment variables:
     ```
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
     The Jira url isnt required, but allows Gerald to check your Jira tickets
     ```
     JIRA_URL='https://example.atlassian.net/jira/software/projects/example/boards/2/backlog?assignee=person'

## Usage

### Running the Application

To start the virtual assistant, run the following command:
```bash
python main.py
```

### Interacting with the Assistant

- **GUI**: Use the graphical user interface to interact with the assistant.

### Example Commands

- **Send a Message**: "Send a message to John"
- **Open an Application**: "Open Chrome"
- **Read Emails**: "Read my emails"
- **Ask about on-screen information**: "Make a summary of this paragraph"

## Code Structure

- `main.py`: Contains the main logic for running the assistant and the GUI.
- NOT WORKING:`learn.py`: Includes the `ComputerUseAgent` class for processing tool use requests.
- `functions.py`: Contains utility functions for interacting with the system and applications.
- `funcList.py`: Defines the list of available functions and their parameters.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the developers of the libraries and tools used in this project.
