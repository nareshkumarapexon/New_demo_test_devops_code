x = [1, 2, 3, 4, 5]

colors = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Purple
    "\033[96m",  # Cyan
]

def color():
    import random
    return random.choice(colors)

# Print each item in random color
for i in x:
    
    print(color() + str(i*i))
