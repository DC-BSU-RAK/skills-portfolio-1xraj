import tkinter as tk
from tkinter import messagebox
import random
import os

# Pillow for reliable image loading
from PIL import Image, ImageTk


# ----------------------------
# GLOBAL STATE
# ----------------------------
bg_img = None            # background image
wrong_questions = []     # list of questions where you made at least one mistake
questionMarkedWrong = False  # avoids logging same question multiple times


# ----------------------------
# LOAD BACKGROUND IMAGE
# ----------------------------
def loadBackground():
    """
    Load backgrounddark.png using Pillow.
    If anything fails, bg_img stays None and we use a solid color.
    """
    global bg_img

    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "backgrounddark.png")

    try:
        img = Image.open(img_path)                    # open the image file
        img = img.resize((500, 500), Image.LANCZOS)   # resize to window size
        bg_img = ImageTk.PhotoImage(img)              # convert to Tk image
        print("Loaded background:", img_path)
        return True
    except Exception as e:
        print("Error loading background image:", e)
        bg_img = None
        return False


# ----------------------------
# MAIN MENU (startup screen)
# ----------------------------
def displayMenu():
    """Show the startup screen with title and difficulty options."""
    clear()

    # Title with brain emoji
    canvas.create_text(
        250, 60,
        text="🧠 Math Quiz",
        fill="white",
        font=("Arial", 30, "bold")
    )

    # Subheading
    canvas.create_text(
        250, 105,
        text="Choose your difficulty",
        fill="#DDDDDD",
        font=("Arial", 16, "italic")
    )

    # "Select Difficulty" label (subtle grey)
    canvas.create_text(
        250, 145,
        text="Select Difficulty",
        fill="#BBBBBB",
        font=("Arial", 20, "bold")
    )

    # Buttons styled to match black & white theme, with slight accent colors
    btn_easy = tk.Button(
        root,
        text="Easy (1-digit)",
        width=18,
        fg="#A8FF60",          # soft green text
        bg="#111111",
        activebackground="#222222",
        activeforeground="#A8FF60",
        relief="raised",
        command=lambda: startQuiz("easy")
    )

    btn_medium = tk.Button(
        root,
        text="Medium (2-digit)",
        width=18,
        fg="#FFD700",          # gold/yellow text
        bg="#111111",
        activebackground="#222222",
        activeforeground="#FFD700",
        relief="raised",
        command=lambda: startQuiz("medium")
    )

    btn_hard = tk.Button(
        root,
        text="Hard (4-digit)",
        width=18,
        fg="#FF6B6B",          # soft red text
        bg="#111111",
        activebackground="#222222",
        activeforeground="#FF6B6B",
        relief="raised",
        command=lambda: startQuiz("hard")
    )

    canvas.create_window(250, 190, window=btn_easy)
    canvas.create_window(250, 235, window=btn_medium)
    canvas.create_window(250, 280, window=btn_hard)


# ----------------------------
# QUIZ MECHANICS
# ----------------------------
def randomInt(level):
    if level == "easy":
        return random.randint(1, 9)
    elif level == "medium":
        return random.randint(10, 99)
    else:
        return random.randint(1000, 9999)


def decideOperation():
    return random.choice(["+", "-"])


def updateProgressBar():
    """Draw/update the top progress bar for 10 questions (white to match B/W theme)."""
    canvas.delete("progress")
    x0, y0, x1, y1 = 50, 20, 450, 35

    # Outline
    canvas.create_rectangle(x0, y0, x1, y1,
                            outline="white", width=2, tags="progress")

    completed = max(0, questionCount - 1)
    ratio = completed / 10
    fill_x1 = x0 + (x1 - x0) * ratio

    if completed > 0:
        # White bar for B/W look
        canvas.create_rectangle(x0, y0, fill_x1, y1,
                                fill="white", width=0, tags="progress")


def displayProblem():
    """Show one math question."""
    global num1, num2, op, attemptsLeft, answerEntry, submitBtn
    global problemTextID, btn_menu, questionMarkedWrong

    clear()
    updateProgressBar()

    attemptsLeft = 3
    questionMarkedWrong = False

    num1 = randomInt(difficulty)
    num2 = randomInt(difficulty)
    op = decideOperation()

    # Question counter
    canvas.create_text(
        250, 60,
        text=f"Question {questionCount}/10",
        fill="white",
        font=("Arial", 22, "bold")
    )

    # Problem text
    problemTextID = canvas.create_text(
        250, 140,
        text=f"{num1} {op} {num2} = ?",
        fill="white",
        font=("Arial", 28, "bold")
    )

    # Attempts
    canvas.create_text(
        250, 200,
        text=f"Attempts Left: {attemptsLeft}",
        fill="#CCCCCC",
        font=("Arial", 16),
        tags="attempts"
    )

    # Answer entry and submit button
    answerEntry = tk.Entry(root, font=("Arial", 20), width=6, justify="center")
    submitBtn = tk.Button(
        root,
        text="Submit",
        font=("Arial", 14),
        bg="#111111",
        fg="white",
        activebackground="#222222",
        activeforeground="white",
        command=isCorrect
    )

    canvas.create_window(250, 250, window=answerEntry)
    canvas.create_window(250, 300, window=submitBtn)

    # Main menu button
    btn_menu = tk.Button(
        root,
        text="Main Menu",
        font=("Arial", 10),
        bg="#111111",
        fg="#CCCCCC",
        activebackground="#222222",
        activeforeground="white",
        command=displayMenu
    )
    canvas.create_window(250, 350, window=btn_menu)


def flashEffect(color):
    """
    Show a quick colored flash over the whole window.
    (We pass 'white' for correct, 'black' for wrong to fit B/W theme.)
    """
    flash = canvas.create_rectangle(
        0, 0, 500, 500,
        fill=color,
        stipple="gray25"
    )
    root.after(150, lambda: canvas.delete(flash))


def showResultSymbol(is_correct):
    """Show a ✓ or ✗ briefly near the top."""
    symbol = "✓" if is_correct else "✗"
    # keep some color for readability on B/W background
    color = "lightgreen" if is_correct else "red"

    symbol_id = canvas.create_text(
        250, 100,
        text=symbol,
        fill=color,
        font=("Arial", 40, "bold")
    )
    root.after(400, lambda: canvas.delete(symbol_id))


def updateAttempts():
    canvas.delete("attempts")
    canvas.create_text(
        250, 200,
        text=f"Attempts Left: {attemptsLeft}",
        fill="#CCCCCC",
        font=("Arial", 16),
        tags="attempts"
    )


def restartQuiz():
    """Restart full quiz with same difficulty."""
    global score, questionCount, wrong_questions
    score = 0
    questionCount = 1
    wrong_questions = []
    displayProblem()


def isCorrect():
    """Check answer, update score/attempts, log mistakes."""
    global score, attemptsLeft, questionCount, wrong_questions, questionMarkedWrong

    try:
        userAns = int(answerEntry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a number!")
        return

    correct = num1 + num2 if op == "+" else num1 - num2

    if userAns == correct:
        score += 10
        flashEffect("white")          # white flash for correct
        showResultSymbol(True)
        messagebox.showinfo("Correct!", "Nice! +10 points")
        nextQuestion()
    else:
        attemptsLeft -= 1
        flashEffect("black")          # black flash for wrong
        showResultSymbol(False)

        if not questionMarkedWrong:
            wrong_questions.append({
                "qnum": questionCount,
                "text": f"{num1} {op} {num2}",
                "answer": correct
            })
            questionMarkedWrong = True

        if attemptsLeft > 0:
            messagebox.showwarning(
                "Incorrect",
                f"Wrong! Try again.\nAttempts left: {attemptsLeft}"
            )
            updateAttempts()
        else:
            messagebox.showerror(
                "Incorrect",
                f"No attempts left!\nCorrect answer was {correct}\nQuiz restarting."
            )
            restartQuiz()


def nextQuestion():
    global questionCount
    questionCount += 1
    if questionCount > 10:
        displayResults()
    else:
        displayProblem()


def displayResults():
    """Show final score, grade and summary of wrong questions."""
    clear()

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    canvas.create_text(
        250, 120,
        text="Quiz Complete!",
        fill="white",
        font=("Arial", 30, "bold")
    )
    canvas.create_text(
        250, 180,
        text=f"Final Score: {score}/100",
        fill="white",
        font=("Arial", 24)
    )
    canvas.create_text(
        250, 220,
        text=f"Grade: {grade}",
        fill="#CCCCCC",
        font=("Arial", 22)
    )

    if wrong_questions:
        summary_lines = ["Questions you struggled with:"]
        for item in wrong_questions:
            summary_lines.append(
                f"Q{item['qnum']}: {item['text']} = {item['answer']}"
            )
        summary_text = "\n".join(summary_lines)

        canvas.create_text(
            250, 320,
            text=summary_text,
            fill="white",
            font=("Arial", 12),
            justify="center"
        )
    else:
        canvas.create_text(
            250, 320,
            text="Perfect! You answered everything correctly on the first try!",
            fill="lightgreen",
            font=("Arial", 12),
            justify="center"
        )

    btn_again = tk.Button(
        root,
        text="Play Again",
        width=15,
        bg="#111111",
        fg="white",
        activebackground="#222222",
        activeforeground="white",
        command=lambda: startQuiz(difficulty)
    )
    btn_menu = tk.Button(
        root,
        text="Main Menu",
        width=15,
        bg="#111111",
        fg="#CCCCCC",
        activebackground="#222222",
        activeforeground="white",
        command=displayMenu
    )
    btn_exit = tk.Button(
        root,
        text="Exit",
        width=15,
        bg="#111111",
        fg="#FF6B6B",
        activebackground="#222222",
        activeforeground="#FF6B6B",
        command=root.destroy
    )

    canvas.create_window(250, 380, window=btn_again)
    canvas.create_window(250, 420, window=btn_menu)
    canvas.create_window(250, 460, window=btn_exit)


def startQuiz(level):
    """Initialize quiz state and show first problem."""
    global difficulty, score, questionCount, wrong_questions

    difficulty = level
    score = 0
    questionCount = 1
    wrong_questions = []

    displayProblem()


def clear():
    """Clear canvas and redraw background image if available."""
    canvas.delete("all")
    if bg_img:
        canvas.create_image(0, 0, image=bg_img, anchor="nw")


# ----------------------------
# APP SETUP
# ----------------------------
root = tk.Tk()
root.title("Maths Quiz")
root.geometry("500x500")

canvas = tk.Canvas(root, width=500, height=500)
canvas.pack(fill="both", expand=True)

loadBackground()
if bg_img:
    canvas.create_image(0, 0, image=bg_img, anchor="nw")
else:
    canvas.configure(bg="black")

displayMenu()
root.mainloop()
