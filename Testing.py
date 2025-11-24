import time
import random
import os

quotes = [
    "Believe you can and you're halfway there.",
    "Every moment is a fresh beginning.",
    "Dream big. Start small. Act now.",
    "Do something today that your future self will thank you for.",
    "Success is not final, failure is not fatal."
]

colors = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Purple
    "\033[96m",  # Cyan
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def animate_text(text):
    for char in text:
        print(random.choice(colors) + char, end="", flush=True)
        time.sleep(0.05)
    print("\033[0m")  # Reset color

if __name__ == "__main__":
    clear_screen()
    print("\n✨ Motivational Quote Generator ✨\n")
    time.sleep(1)

    quote = random.choice(quotes)
    animate_text(quote)
