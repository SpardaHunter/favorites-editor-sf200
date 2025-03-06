import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import struct

class FavoritesEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Favorites.bin Editor")
        self.max_entries = 10  # Máximo de entradas antes de añadir scroll

        # UI Elements
        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.load_button = tk.Button(root, text="Load Favorites.bin", command=self.load_file)
        self.load_button.pack(pady=5)

        # Frame con scroll
        self.container = tk.Frame(root)
        self.container.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container, height=400)  # Altura fija
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.add_button = tk.Button(root, text="Add Entry", command=self.add_entry)
        self.add_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Save Favorites.bin", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.entries = []  # Lista para almacenar entradas
        self.file_path = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin")])
        if not file_path:
            return

        self.file_path = file_path
        self.file_label.config(text=f"Loaded: {file_path}")

        # Limpiar entradas existentes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        try:
            with open(file_path, "rb") as f:
                data = f.read()

            if len(data) < 4:
                raise ValueError("File too small to be valid.")

            num_entries = struct.unpack_from("<I", data, 0)[0]
            if len(data) != 4 + num_entries * 4:
                raise ValueError("File size does not match the number of entries.")

            offset = 4
            for _ in range(num_entries):
                rom_list, game_index = struct.unpack_from("<HH", data, offset)
                self.add_entry(rom_list, game_index)
                offset += 4

            self.save_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def add_entry(self, rom_list=None, game_index=None):
        frame = tk.Frame(self.scrollable_frame)
        frame.pack(pady=2, fill=tk.X)

        tk.Label(frame, text="ROM List:").pack(side=tk.LEFT, padx=5)
        rom_list_var = tk.IntVar(value=rom_list if rom_list is not None else 1)
        rom_list_entry = tk.Entry(frame, textvariable=rom_list_var, width=5)
        rom_list_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(frame, text="Game Index:").pack(side=tk.LEFT, padx=5)
        game_index_var = tk.IntVar(value=game_index if game_index is not None else 0)
        game_index_entry = tk.Entry(frame, textvariable=game_index_var, width=5)
        game_index_entry.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(frame, text="Remove", command=lambda: self.remove_entry(frame, rom_list_var, game_index_var))
        remove_button.pack(side=tk.RIGHT, padx=5)

        edit_button = tk.Button(frame, text="Edit", command=lambda: self.edit_entry(rom_list_entry, game_index_entry))
        edit_button.pack(side=tk.RIGHT, padx=5)

        self.entries.append((rom_list_var, game_index_var))
        self.update_scroll()

    def remove_entry(self, frame, rom_list_var, game_index_var):
        frame.destroy()
        self.entries = [(rom, game) for rom, game in self.entries if rom != rom_list_var or game != game_index_var]
        self.update_scroll()

    def edit_entry(self, rom_list_entry, game_index_entry):
        rom_list_entry.config(state=tk.NORMAL)
        game_index_entry.config(state=tk.NORMAL)

    def update_scroll(self):
        if len(self.entries) > self.max_entries:
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
        else:
            self.scrollbar.pack_forget()
            self.canvas.configure(yscrollcommand=None)

    def save_file(self):
        if not self.file_path:
            return

        try:
            num_entries = len(self.entries)
            data = struct.pack("<I", num_entries)
            for rom_list_var, game_index_var in self.entries:
                rom_list = rom_list_var.get()
                game_index = game_index_var.get()
                data += struct.pack("<HH", rom_list, game_index)

            with open(self.file_path, "wb") as f:
                f.write(data)

            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FavoritesEditor(root)
    root.mainloop()
