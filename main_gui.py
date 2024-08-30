import customtkinter as ctk
import subprocess
import ollama

# Define a class for interacting with the AI model
class AIChat:
    def __init__(self, model_name):
        self.model_name = model_name
        # self.ensure_model()

    # def ensure_model(self):
    #     """Pull the model if it's not already available."""
    #     try:
    #         result = subprocess.run(["ollama", "pull", self.model_name], check=True, capture_output=True, text=True)
    #         print(f"Model {self.model_name} pulled successfully:\n{result.stdout}")
    #     except subprocess.CalledProcessError as e:
    #         ctk.CTkMessagebox.show_error("Model Error", f"Failed to pull the model {self.model_name}. Error: {e.stderr}")
    #     except FileNotFoundError:
    #         ctk.CTkMessagebox.show_error("CLI Error", "Ollama CLI not found. Ensure that Ollama is installed and in your PATH.")
    #         # exit()

    def generate_response(self, prompt):
        """Generate a response from the AI model using a prompt."""
        try:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"]
        except Exception as e:
            ctk.CTkMessagebox.show_error("API Error", f"An error occurred while generating the response: {e}")
            return None

# Define a class for the GUI application
class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat Application")
        self.root.geometry("800x600")  # Set initial window size
        self.root.minsize(600, 400)  # Set minimum window size
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.ai_chat = AIChat("llama3.1")

        # Create the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Frame for the main content
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Text area to display conversation
        self.text_area = ctk.CTkTextbox(self.main_frame, wrap="word", height=20)
        self.text_area.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Entry frame for the prompt and button
        self.entry_frame = ctk.CTkFrame(self.main_frame)
        self.entry_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.entry_frame.grid_columnconfigure(0, weight=1)

        # Entry field for the user to type prompts
        self.prompt_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your prompt here...", width=600)
        self.prompt_entry.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        self.prompt_entry.bind("<Return>", lambda event: self.send_prompt())

        # Button to send the prompt to the AI
        self.send_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.send_prompt)
        self.send_button.grid(row=0, column=1, padx=5, pady=10)

    def send_prompt(self):
        # Get the user input prompt
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            ctk.CTkMessagebox.show_warning("Input Error", "Please enter a prompt.")
            return

        # Display the user's prompt in the text area
        self.text_area.insert("end", f"User: {prompt}\n")

        # Generate the AI response
        response = self.ai_chat.generate_response(prompt)
        if response:
            # Display the AI's response in the text area
            self.text_area.insert("end", f"AI: {response}\n")

        # Clear the entry field
        self.prompt_entry.delete(0, "end")
        self.text_area.see("end")

# Run the application
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
    root = ctk.CTk()
    app = ChatApp(root)
    root.mainloop()
