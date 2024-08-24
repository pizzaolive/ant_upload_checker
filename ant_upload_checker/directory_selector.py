import tkinter as tk
from tkinter import filedialog
from pathlib import Path


class DirectorySelector:
    def __init__(self):
        self.root = tk.Tk()
        self.folder_listbox = tk.Listbox(
            self.root, selectmode=tk.SINGLE, width=60, height=15
        )

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.folder_listbox.insert(tk.END, folder)

    def get_selected_folders(self) -> list[str]:
        folders = self.folder_listbox.get(0, tk.END)
        self.root.destroy()  # Close the window after selection

        return list(folders)

    def select_multiple_folders(self) -> list[str]:
        self.root.title("Select Multiple Folders")
        self.folder_listbox.pack(pady=20)

        add_button = tk.Button(self.root, text="Add Folder", command=self.add_folder)
        add_button.pack(pady=10)

        save_button = tk.Button(self.root, text="Save Folders", command=self.root.quit)
        save_button.pack(pady=10)

        self.root.mainloop()

        return self.get_selected_folders()
