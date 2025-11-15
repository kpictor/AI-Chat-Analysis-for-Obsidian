
# AI Chat Analysis for Obsidian

This application automatically analyzes chat history files and generates reports in Obsidian. It monitors a specified directory for new or modified chat files, processes them with an AI model, and appends the analysis to a corresponding file in your Obsidian vault.

## Features

- **Automated Analysis**: Analyzes chat files from a specified directory.
- **AI-Powered Insights**: Uses AI models (Gemini or OpenAI) to generate summaries and identify key topics.
- **Obsidian Integration**: Creates and updates analysis reports in your Obsidian vault.
- **GUI Interface**: Provides a simple graphical user interface for configuration and operation.

## How It Works

The application scans a specified directory for `.txt` chat files. When you start the process, it reads the content of each chat file, attempting to decode it using multiple common encodings (UTF-8, GBK, UTF-8-SIG) to handle various file formats robustly. The content is then sent to a configured AI model (Gemini or OpenAI) for analysis. The AI-generated summary is then *appended* to a Markdown file in your Obsidian vault. This ensures that new analyses are added to the end of the file, preserving any existing content and creating a historical record for each chat group.

## Setup and Configuration

### 1. Prerequisites

- Python 3.6 or higher
- A Gemini or OpenAI API key

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ai-chat-analysis-for-obsidian.git
   cd ai-chat-analysis-for-obsidian
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

1.  **Set your API Key as an Environment Variable:**
    It is highly recommended to set your API key as an environment variable (e.g., `GEMINI_API_KEY` or `OPENAI_API_KEY`) rather than entering it directly into the GUI. This enhances security, especially when sharing or versioning your project.

    **For Windows:**
    ```bash
    setx GEMINI_API_KEY "YOUR_API_KEY"
    # or for OpenAI
    setx OPENAI_API_KEY "YOUR_API_KEY"
    ```

    **For macOS/Linux:**
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    # or for OpenAI
    export OPENAI_API_KEY="YOUR_API_KEY"
    ```
    (Note: For permanent changes on macOS/Linux, add the `export` command to your shell's profile file, e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`).

2.  Run the application using `python gui.py`.
3.  In the GUI, click "Browse..." to select your **Chat File Directory** and **Obsidian Vault Directory**.
4.  Select your desired **AI Provider** (Gemini or OpenAI). The application will attempt to load the API key from the corresponding environment variable. If not found, you may be prompted to enter it.
5.  Optionally, customize the **AI Prompt**.
6.  Click **Save Configuration**. Your settings will be saved to `config.json`.

## Usage

To start the application, run the following command in your terminal:

```bash
python gui.py
```

Once the GUI is open, click the "Start Processing" button to begin the analysis of the chat files. The application will process all `.txt` files in the configured directory, and the reports will be written to your Obsidian vault.

## Project Structure

- `app.py`: The main application file containing the core analysis logic.
- `gui.py`: The graphical user interface for the application.
- `config.json`: Stores the user's configuration settings.
- `requirements.txt`: A list of the required Python libraries and dependencies.
- `README.md`: This file, providing an overview and instructions for the project.
- `chat_files/`: The directory where your chat history files are stored.
- `obsidian_vault/`: The directory where your Obsidian vault is located.

## Security Considerations

**Protecting your API Key:** Your API key grants access to AI services and should be treated with utmost confidentiality. Avoid hardcoding it directly into your scripts or committing it to version control. Using environment variables, as described in the Configuration section, is the recommended secure practice.

**`config.json` File:** The `config.json` file stores your application settings, including potentially sensitive information if you choose not to use environment variables for your API key. It is strongly recommended to add `config.json` to your `.gitignore` file to prevent it from being accidentally committed to your repository.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
