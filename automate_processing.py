
import os
import json
import sys
import threading

# Add the current directory to the path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import process_chat_files, load_config

def automate_processing():
    """
    Automates the processing of chat files by iterating through a range of directories,
    updating the configuration file, and running the processing script for each directory.
    """
    # Base path for the Wechat directories
    wechat_base_path = r"C:/Users/Dicrix/Desktop/Wechat"
    
    # Path to the configuration file
    config_path = "config.json"

    # Get a list of directories to process
    directories_to_process = [f"{i}cut folder" for i in range(51, 267)]

    for dir_name in directories_to_process:
        # Construct the full path to the chat file directory
        chat_file_dir = os.path.join(wechat_base_path, dir_name)
        chat_file_dir = chat_file_dir.replace('\\', '/') # Ensure forward slashes for consistency

        if not os.path.isdir(chat_file_dir):
            print(f"Directory not found: {chat_file_dir}. Skipping.")
            continue

        print(f"Processing directory: {chat_file_dir}")

        try:
            # Load the existing configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Update the chat file directory
            config["CHAT_FILE_DIR"] = chat_file_dir

            # Write the updated configuration back to the file
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"Updated config.json with new directory: {chat_file_dir}")

            # Create a dummy stop event
            stop_event = threading.Event()

            # Define dummy callback functions
            def log_callback(message):
                print(f"LOG: {message}")

            def status_callback(message):
                print(f"STATUS: {message}")

            # Run the processing function
            process_chat_files(log_callback, status_callback, stop_event)

            print(f"Finished processing directory: {chat_file_dir}")

        except Exception as e:
            print(f"An error occurred while processing {dir_name}: {e}")

    print("Automation complete.")

if __name__ == "__main__":
    automate_processing()
