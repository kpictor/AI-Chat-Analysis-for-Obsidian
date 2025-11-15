
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
from app import process_chat_files, validate_api_key

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Analysis for Obsidian")
        self.root.geometry("600x650")
        self.processing_thread = None
        self.stop_event = threading.Event()

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # --- Configuration Frame ---
        config_frame = tk.LabelFrame(self.root, text="Configuration", padx=10, pady=10)
        config_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(config_frame, text="Chat File Directory:").grid(row=0, column=0, sticky="w")
        self.chat_dir_entry = tk.Entry(config_frame, width=50)
        self.chat_dir_entry.grid(row=0, column=1, padx=5, columnspan=2)
        tk.Button(config_frame, text="Browse...", command=self.browse_chat_dir).grid(row=0, column=3)

        tk.Label(config_frame, text="Obsidian Vault Directory:").grid(row=1, column=0, sticky="w")
        self.obsidian_dir_entry = tk.Entry(config_frame, width=50)
        self.obsidian_dir_entry.grid(row=1, column=1, padx=5, columnspan=2)
        tk.Button(config_frame, text="Browse...", command=self.browse_obsidian_dir).grid(row=1, column=3)
        
        # --- AI Provider Frame ---
        provider_frame = tk.LabelFrame(self.root, text="AI Provider", padx=10, pady=10)
        provider_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(provider_frame, text="Provider:").grid(row=0, column=0, sticky="w")
        self.provider_var = tk.StringVar(value="Gemini")
        self.provider_menu = ttk.Combobox(provider_frame, textvariable=self.provider_var, values=["Gemini", "OpenAI"], state="readonly")
        self.provider_menu.grid(row=0, column=1, padx=5, sticky="w")
        self.provider_menu.bind("<<ComboboxSelected>>", self.update_api_key_display)
        
        tk.Label(provider_frame, text="API Key:").grid(row=1, column=0, sticky="w")
        self.api_key_entry = tk.Entry(provider_frame, width=40, show="*")
        self.api_key_entry.grid(row=1, column=1, padx=5)
        tk.Button(provider_frame, text="Validate", command=self.validate_key).grid(row=1, column=2)

        tk.Label(provider_frame, text="Model:").grid(row=2, column=0, sticky="w")
        self.model_var = tk.StringVar()
        self.model_menu = ttk.Combobox(provider_frame, textvariable=self.model_var, state="disabled", width=40)
        self.model_menu.grid(row=2, column=1, padx=5, sticky="w")
        
        tk.Label(provider_frame, text="AI Prompt:").grid(row=3, column=0, sticky="nw")
        self.prompt_text = tk.Text(provider_frame, width=60, height=10, wrap="word")
        self.prompt_text.grid(row=3, column=1, padx=5, pady=5, columnspan=2, sticky="nsew")
        provider_frame.grid_rowconfigure(3, weight=1)
        provider_frame.grid_columnconfigure(1, weight=1)

        tk.Button(self.root, text="Save Configuration", command=self.save_config).pack(pady=5)
        
        # --- Control Frame ---
        control_frame = tk.LabelFrame(self.root, text="Controls", padx=10, pady=10)
        control_frame.pack(padx=10, pady=10, fill="x")

        self.start_button = tk.Button(control_frame, text="Start Processing", command=self.start_processing_thread)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop Processing", command=self.stop_processing, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # --- Status Frame ---
        status_frame = tk.LabelFrame(self.root, text="Status Log", padx=10, pady=10)
        status_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.status_text = tk.Text(status_frame, wrap="word", state="disabled")
        self.status_text.pack(fill="both", expand=True)

        self.status_bar = tk.Label(self.root, text="Status: Idle", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_chat_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.chat_dir_entry.delete(0, tk.END)
            self.chat_dir_entry.insert(0, directory)

    def browse_obsidian_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.obsidian_dir_entry.delete(0, tk.END)
            self.obsidian_dir_entry.insert(0, directory)

    def load_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
                
                self.chat_dir_entry.delete(0, tk.END)
                self.chat_dir_entry.insert(0, self.config.get("CHAT_FILE_DIR", ""))
                
                self.obsidian_dir_entry.delete(0, tk.END)
                self.obsidian_dir_entry.insert(0, self.config.get("OBSIDIAN_VAULT_DIR", ""))
                
                provider = self.config.get("AI_PROVIDER", "Gemini")
                self.provider_var.set(provider)
                self.update_api_key_display()

                self.model_var.set(self.config.get(f"{provider.upper()}_MODEL", ""))
                
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert(tk.END, self.config.get("AI_PROMPT", ""))
        except FileNotFoundError:
            self.config = {}
            self.log_status("Configuration file not found. Please save your settings.")
        except json.JSONDecodeError:
            self.config = {}
            self.log_status("Error reading configuration file. Please check its format.")

    def save_config(self):
        provider = self.provider_var.get()
        self.config["CHAT_FILE_DIR"] = self.chat_dir_entry.get()
        self.config["OBSIDIAN_VAULT_DIR"] = self.obsidian_dir_entry.get()
        self.config["AI_PROVIDER"] = provider
        self.config[f"{provider.upper()}_API_KEY"] = self.api_key_entry.get()
        self.config[f"{provider.upper()}_MODEL"] = self.model_var.get()
        self.config["AI_PROMPT"] = self.prompt_text.get("1.0", tk.END).strip()
        
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log_status("Configuration saved successfully.")
            return True
        except Exception as e:
            self.log_status(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Error saving configuration: {e}")
            return False

    def update_api_key_display(self, event=None):
        provider = self.provider_var.get()
        api_key = self.config.get(f"{provider.upper()}_API_KEY", "")
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)
        self.model_menu.set(self.config.get(f"{provider.upper()}_MODEL", ""))
        self.model_menu.config(state="disabled")

    def validate_key(self):
        provider = self.provider_var.get()
        api_key = self.api_key_entry.get()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key.")
            return

        self.log_status(f"Validating {provider} API key...")
        self.set_status(f"Status: Validating {provider} Key...")
        
        # Run validation in a separate thread to keep GUI responsive
        threading.Thread(target=self._validate_key_thread, args=(provider, api_key), daemon=True).start()

    def _validate_key_thread(self, provider, api_key):
        models = validate_api_key(provider, api_key)
        
        def update_gui():
            if models:
                self.log_status("API key is valid.")
                self.model_menu['values'] = models
                self.model_menu.config(state="readonly")
                # Try to set the saved model, otherwise set to first in list
                saved_model = self.config.get(f"{provider.upper()}_MODEL")
                if saved_model in models:
                    self.model_var.set(saved_model)
                elif models:
                    self.model_var.set(models[0])
                messagebox.showinfo("Success", "API key is valid.")
            else:
                self.log_status("API key is invalid or failed to fetch models.")
                self.model_menu.set("")
                self.model_menu.config(state="disabled")
                messagebox.showerror("Error", "API key is invalid or no models found.")
            self.set_status("Status: Idle")
        
        self.root.after(0, update_gui)

    def start_processing_thread(self):
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showwarning("In Progress", "Processing is already in progress.")
            return
            
        if not self.save_config():
            messagebox.showerror("Error", "Could not start processing due to configuration save failure.")
            return

        self.stop_event.clear()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.processing_thread = threading.Thread(target=self._process_files_wrapper, daemon=True)
        self.processing_thread.start()

    def stop_processing(self):
        if self.processing_thread and self.processing_thread.is_alive():
            self.stop_event.set()
            self.log_status("Stop signal sent. Finishing current file...")

    def _process_files_wrapper(self):
        process_chat_files(self.log_status, self.set_status, self.stop_event)
        
        def update_gui_buttons():
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
        
        self.root.after(0, update_gui_buttons)

    def log_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.config(state="disabled")
        self.status_text.see(tk.END)

    def set_status(self, message):
        self.status_bar.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
