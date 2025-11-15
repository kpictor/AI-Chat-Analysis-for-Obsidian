
import time

import os

import json

import glob

import google.generativeai as genai

import openai



def load_config():



    """Loads the configuration from config.json."""



    with open("config.json", "r", encoding="utf-8") as f:



        return json.load(f)



def validate_api_key(provider, api_key):

    """Validates the API key and fetches available models."""

    try:

        if provider == "Gemini":

            genai.configure(api_key=api_key)

            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

            return [model.replace("models/", "") for model in models]

        elif provider == "OpenAI":

            openai.api_key = api_key

            models = openai.Model.list()

            return [model.id for model in models['data']]

    except Exception as e:

        print(f"API key validation failed for {provider}: {e}")

        return None



def read_file_with_encodings(file_path, encodings=['utf-8', 'gbk', 'utf-8-sig', 'latin-1']):
    """Tries to read a file with a list of encodings."""
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(encoding, b'', 0, 0, f"Could not decode file {file_path} with any of the tried encodings.")

def analyze_chat(file_path, config, log_callback, status_callback):

    """Analyzes a single chat file using the configured AI provider."""

    provider = config.get("AI_PROVIDER", "Gemini")

    try:
        status_callback(f"Status: Analyzing {os.path.basename(file_path)} with {provider}...")
        content = read_file_with_encodings(file_path)

        prompt = config.get("AI_PROMPT", "Please analyze the following chat history.")
        full_prompt = f"{prompt}\n\n{content}"

        analysis = ""
        if provider == "Gemini":
            api_key = config.get("GEMINI_API_KEY")
            model_name = config.get("GEMINI_MODEL", "gemini-pro")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            analysis = response.text
        elif provider == "OpenAI":
            api_key = config.get("OPENAI_API_KEY")
            model_name = config.get("OPENAI_MODEL", "gpt-3.5-turbo")
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ]
            )
            analysis = response.choices[0].message['content']

        log_callback(f"Successfully analyzed file: {os.path.basename(file_path)}")
        return analysis

    except Exception as e:
        log_callback(f"Error analyzing file {file_path}: {e}")
        status_callback(f"Status: Error during analysis of {os.path.basename(file_path)}")
        return None



def write_to_obsidian(group_name, analysis_content, config, log_callback):

    """Writes the analysis content to a file in the Obsidian vault."""

    try:

        obsidian_vault_dir = config["OBSIDIAN_VAULT_DIR"]

        file_name = f"{group_name} Chat Analysis.md"

        file_path = os.path.join(obsidian_vault_dir, file_name)


        os.makedirs(obsidian_vault_dir, exist_ok=True)

        with open(file_path, 'a', encoding='utf-8') as f:

            f.write(f"### Analysis for {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(analysis_content)
            
            f.write("\n\n")

        log_callback(f"Successfully wrote analysis for {group_name} to Obsidian.")

    except Exception as e:

        log_callback(f"Error writing to Obsidian for group {group_name}: {e}")
def process_chat_files(log_callback, status_callback, stop_event):



    """Scans the directory, analyzes each chat file, and writes to Obsidian."""



    try:



        log_callback("Starting processing...")



        config = load_config()



        chat_file_dir = config["CHAT_FILE_DIR"]



        obsidian_vault_dir = config["OBSIDIAN_VAULT_DIR"]



        



        if not os.path.isdir(chat_file_dir):



            log_callback(f"Error: Chat file directory not found at {chat_file_dir}")



            status_callback("Status: Error")



            return







        chat_files = glob.glob(os.path.join(chat_file_dir, "*.txt"))



        



        if not chat_files:



            log_callback("No .txt files found in the directory.")



            status_callback("Status: Idle")



            return







        total_files = len(chat_files)



        log_callback(f"Found {total_files} chat file(s) to process.")







        for i, file_path in enumerate(chat_files):
            if stop_event.is_set():
                log_callback("Processing stopped by user.")
                status_callback("Status: Idle")
                break
        
            group_name = os.path.splitext(os.path.basename(file_path))[0]
        
            log_callback(f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}")
            
            analysis = analyze_chat(file_path, config, log_callback, status_callback)
            if analysis:
                write_to_obsidian(group_name, analysis, config, log_callback)



        



        log_callback("Processing complete.")



        status_callback("Status: Idle")



    except Exception as e:



        log_callback(f"An unexpected error occurred: {e}")



        status_callback("Status: Error")








