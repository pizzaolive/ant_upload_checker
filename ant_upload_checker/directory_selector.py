import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import logging


class DirectorySelector:
    def __init__(self) -> None:
        self.root = tk.Tk()

    def add_folder(self) -> None:
        """
        Open a dialog to select a given directory, add it to the listbox
        """
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.folder_listbox.insert(tk.END, folder)

    def select_input_directories(self) -> list[str]:
        """
        Provide a UI for the user to select multiple input directories to be scanned
        """
        logging.info(
            "In the dialog box, please select one or more directories containing your films"
        )

        self.root.deiconify()
        self.folder_listbox = tk.Listbox(
            self.root,
            selectmode=tk.SINGLE,
            width=60,
            height=15,
        )

        self.root.title("Select one or more input directories containing your films")
        self.folder_listbox.pack(pady=20)

        add_button = tk.Button(self.root, text="Add Folder", command=self.add_folder)
        add_button.pack(pady=10)

        save_button = tk.Button(self.root, text="Save Folders", command=self.root.quit)
        save_button.pack(pady=10)

        self.root.mainloop()
        input_directories = list(self.folder_listbox.get(0, tk.END))

        # Hide but don't close
        self.root.withdraw()

        return input_directories

    def select_output_directory(self) -> str:
        """
        Provide a UI for the user to select a single output directory
        where the film list csv will later be saved.
        """
        self.root.withdraw()
        logging.info("In the dialog box, please select your output directory")
        output_directory = filedialog.askdirectory(
            title="Please select your output directory",
        )

        # Hide but don't close
        self.root.withdraw()

        return output_directory

    def run_directory_selector(self) -> tuple[list[str], str]:
        """
        Prompt user to select multiple input directories, then a single output directory,
        then close the Tkinter root window
        """
        input_directories = self.select_input_directories()
        output_directory = self.select_output_directory()

        self.root.destroy()

        return input_directories, output_directory
