import tkinter as tk
from tkinter import filedialog, Text, simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import json

class SOPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SOP Maker")
        self.root.geometry("800x600")  # Set initial size of the window

        # Create a folder for the SOPs if it doesn't exist
        self.sop_dir = 'sops'
        if not os.path.exists(self.sop_dir):
            os.makedirs(self.sop_dir)

        # Create a menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Create a 'File' menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        # Add commands to the 'File' menu
        file_menu.add_command(label="Save SOP", command=self.save_sop)
        file_menu.add_command(label="Load SOP", command=self.load_sop)

        # Create a main frame which contains a canvas and a scrollbar
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create another frame inside the canvas to hold the content
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.content_frame, anchor="nw")

        # Add buttons for adding steps, saving, and loading SOPs
        self.add_step_btn = ttk.Button(self.content_frame, text="Add Step", command=self.add_sop_step)
        self.add_step_btn.pack(pady=10)
        self.steps = []  # To keep track of steps added

    def add_sop_step(self):
        """Add entries for a new step with title, summary, and an option to add an image."""
        step_frame = ttk.Frame(self.content_frame)
        step_frame.pack(pady=10, padx=10, fill=tk.X)

        title = ttk.Label(step_frame, text="Title:")
        title.grid(row=0, column=0)
        title_entry = ttk.Entry(step_frame, width=40)
        title_entry.grid(row=0, column=1, sticky=tk.W)

        summary = ttk.Label(step_frame, text="Summary:")
        summary.grid(row=1, column=0)
        summary_entry = tk.Text(step_frame, width=30, height=4)
        summary_entry.grid(row=1, column=1)

        # Placeholder for the image
        image_label = ttk.Label(step_frame, text="No Image", width=20)
        image_label.grid(row=0, column=2, rowspan=2)

        # Function to handle image uploading
        def upload_image():
            file_path = filedialog.askopenfilename()
            if file_path:
                image = Image.open(file_path)
                image.thumbnail((100, 100))  # Resize the image to fit into the interface
                photo = ImageTk.PhotoImage(image)
                image_label.config(image=photo)
                image_label.image = photo  # Keep a reference to avoid garbage collection
                image_label.image_path = file_path  # Store the image file path

        upload_btn = ttk.Button(step_frame, text="Upload Image", command=upload_image)
        upload_btn.grid(row=2, column=2)

        # Add this step frame to the steps list
        self.steps.append({
            'frame': step_frame, 'title': title_entry,
            'summary': summary_entry, 'image': image_label
        })

    def save_sop(self):
        """Save the SOP with all its steps."""
        sop = []
        for step in self.steps:
            title = step['title'].get()
            summary = step['summary'].get("1.0", tk.END).strip()
            image_path = getattr(step['image'], 'image_path', '')
            
            if not title:
                messagebox.showerror("Error", "Each step must have a title.")
                return

            sop.append({
                'title': title,
                'summary': summary,
                'image': image_path
            })

        sop_name = simpledialog.askstring("SOP Name", "Enter a name for this SOP:")
        if sop_name:
            sop_path = os.path.join(self.sop_dir, f"{sop_name}.json")
            with open(sop_path, 'w') as sop_file:
                json.dump(sop, sop_file, indent=4)

            messagebox.showinfo("Saved", "Your SOP has been saved successfully.")

    def load_sop(self):
        """Load an existing SOP."""
        sop_path = filedialog.askopenfilename(initialdir=self.sop_dir, filetypes=[("JSON files", "*.json")])
        if sop_path:
            with open(sop_path, 'r') as sop_file:
                sop = json.load(sop_file)

            # Clear current steps
            for step in self.steps:
                step['frame'].destroy()
            self.steps.clear()

            # Load and display the SOP steps
            for step_info in sop:
                self.add_sop_step()  # Create an entry for each step
                step = self.steps[-1]  # Get the step we just added
                step['title'].insert(0, step_info['title'])
                step['summary'].insert(tk.END, step_info['summary'])

                if step_info['image']:
                    image = Image.open(step_info['image'])
                    image.thumbnail((100, 100))
                    photo = ImageTk.PhotoImage(image)
                    step['image'].config(image=photo)
                    step['image'].image = photo  # Keep a reference
                    step['image'].image_path = step_info['image']  # Store the image path

# Create the main application window
root = tk.Tk()

# Set the window size here
root.geometry("800x600")  # Width x Height

app = SOPApp(root)
root.mainloop()
