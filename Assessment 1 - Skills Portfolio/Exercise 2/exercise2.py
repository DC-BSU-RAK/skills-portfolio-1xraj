import tkinter as tk
from tkinter import messagebox
import random
import os


def load_jokes():
    """Load jokes from randomJokes.txt in the same folder as this script."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "randomJokes.txt")

        with open(file_path, "r", encoding="utf-8") as f:
            jokes = [line.strip() for line in f.readlines() if line.strip()]

        return jokes
    except FileNotFoundError:
        messagebox.showerror("Error", "randomJokes.txt not found in the same folder as this script.")
        return []


def parse_joke(line):
    """Split a joke into (setup, punchline)."""
    if "?" in line:
        setup, punchline = line.split("?", 1)
        return setup.strip() + "?", punchline.strip()
    return line.strip(), "(No punchline found)"


def build_app(root):
    root.title("Alexa Joke Assistant")
    root.geometry("550x400")
    root.config(bg="#FFF8DC")

    jokes = load_jokes()

    # app state kept in a dict instead of instance variables
    state = {
        "current_setup": "",
        "current_punchline": ""
    }

    setup_var = tk.StringVar(value="")
    punchline_var = tk.StringVar(value="")

    title_label = tk.Label(
        root, text=" Alexa Joke Assistant ",
        font=("Comic Sans MS", 26, "bold"),
        bg="#FFF8DC", fg="#FF6347"
    )
    title_label.pack(pady=(20, 10))

    setup_label = tk.Label(
        root, textvariable=setup_var,
        font=("Arial", 18, "bold"),
        wraplength=500,
        bg="#FFF8DC", fg="#4682B4"
    )
    setup_label.pack(pady=(10, 5))

    punchline_label = tk.Label(
        root, textvariable=punchline_var,
        font=("Arial", 16, "italic"),
        wraplength=500,
        bg="#FFF8DC", fg="#32CD32"
    )
    punchline_label.pack(pady=(5, 20))

    button_style = {
        "font": ("Arial", 12, "bold"),
        "bg": "#FFB74D",
        "fg": "black",
        "activebackground": "#FFA726",
        "activeforeground": "white",
        "relief": "raised",
        "bd": 2,
        "padx": 10,
        "pady": 5
    }

    def show_joke():
        if not jokes:
            return
        line = random.choice(jokes)
        setup, punchline = parse_joke(line)

        state["current_setup"] = setup
        state["current_punchline"] = punchline

        setup_var.set(setup)
        punchline_var.set("")  # clear punchline until asked

    def show_punchline():
        if state["current_punchline"]:
            punchline_var.set(state["current_punchline"])
        else:
            punchline_var.set("No punchline available.")

    btn_frame = tk.Frame(root, bg="#FFF8DC")
    btn_frame.pack(pady=(10, 25))

    tk.Button(btn_frame, text="Tell me a Joke", command=show_joke, width=15, **button_style).grid(row=0, column=0, padx=8, pady=5)
    tk.Button(btn_frame, text="Show Punchline", command=show_punchline, width=15, **button_style).grid(row=0, column=1, padx=8, pady=5)
    tk.Button(btn_frame, text="Next Joke", command=show_joke, width=15, **button_style).grid(row=0, column=2, padx=8, pady=5)

    tk.Button(
        root, text="Quit", command=root.quit, width=12,
        font=("Arial", 12, "bold"),
        bg="#FF5733", fg="white",
        activebackground="#FA0202", activeforeground="white",
        relief="raised", bd=2, padx=10, pady=5
    ).pack(pady=(10, 15))

    # optional: load one joke immediately
    show_joke()


if __name__ == "__main__":
    root = tk.Tk()
    build_app(root)
    root.mainloop()
