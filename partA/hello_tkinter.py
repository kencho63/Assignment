import tkinter as tk

root = tk.Tk()
root.title("Hello Tkinter")
label = tk.Label(root, text="Hello!")
label.pack(padx=40, pady=10)
button = tk.Button(root, text="Click me",
                   command=lambda: label.config(text="Button clicked!"))  # callback
button.pack(pady=10)
root.mainloop()
