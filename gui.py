import sys
import tkinter as tk
from tkinter import messagebox, ttk
from generator import PasswordConfig, PasswordGenerator

class PasswordGeneratorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔐 Secure Password Generator")
        self.root.geometry("620 x 680")
        self.root.minsize(540, 600)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.setup_ui()
        self.generate_password()

    def setup_ui(self):
        # Colors
        BG_COLOR = "#f8f9fa"
        PRIMARY_COLOR = "#2563eb"
        CARD_BG = "#ffffff"
        
        self.root.configure(bg=BG_COLOR)
        
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        title_label = tk.Label(
            main_frame,
            text="🔐 Secure Password Generator",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg="#1e293b"
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # Password Display Card
        display_card = tk.Frame(main_frame, bg=CARD_BG, bd=1, relief="solid", highlightthickness=0)
        display_card.pack(fill=tk.X, pady=(0, 15), ipady=10, ipadx=10)

        # Password Output Entry
        entry_frame = tk.Frame(display_card, bg=CARD_BG)
        entry_frame.pack(fill=tk.X, padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            entry_frame,
            textvariable=self.password_var,
            font=("Consolas", 16, "bold"),
            bd=1,
            relief="flat",
            bg="#f1f5f9",
            fg="#0f172a",
            selectbackground="#cbd5e1"
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        # Copy Button
        copy_btn = tk.Button(
            entry_frame,
            text="📋 Copy",
            font=("Segoe UI", 10, "bold"),
            bg="#3b82f6",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.copy_password
        )
        copy_btn.pack(side=tk.RIGHT)

        # Strength Indicator
        strength_frame = tk.Frame(display_card, bg=CARD_BG)
        strength_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.strength_label = tk.Label(
            strength_frame,
            text="Strength: Unknown",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg="#64748b"
        )
        self.strength_label.pack(side=tk.LEFT)

        self.entropy_label = tk.Label(
            strength_frame,
            text="0 bits entropy",
            font=("Segoe UI", 9),
            bg=CARD_BG,
            fg="#94a3b8"
        )
        self.entropy_label.pack(side=tk.RIGHT)

        # Strength Meter Bar Canvas
        self.meter_canvas = tk.Canvas(display_card, height=8, bg="#e2e8f0", bd=0, highlightthickness=0)
        self.meter_canvas.pack(fill=tk.X, padx=10, pady=(6, 0))
        self.meter_bar = self.meter_canvas.create_rectangle(0, 0, 0, 8, fill="#cbd5e1", width=0)

        # Settings Card
        settings_card = tk.LabelFrame(
            main_frame,
            text=" Password Configuration ",
            font=("Segoe UI", 11, "bold"),
            bg=CARD_BG,
            fg="#334155",
            padx=15,
            pady=15
        )
        settings_card.pack(fill=tk.X, pady=(0, 15))

        # Length Slider & Spinbox
        length_frame = tk.Frame(settings_card, bg=CARD_BG)
        length_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(length_frame, text="Password Length:", font=("Segoe UI", 10), bg=CARD_BG).pack(side=tk.LEFT)

        self.length_var = tk.IntVar(value=16)
        
        length_spin = tk.Spinbox(
            length_frame,
            from_=4,
            to=128,
            textvariable=self.length_var,
            width=5,
            font=("Segoe UI", 10, "bold"),
            command=self.on_length_spin_change
        )
        length_spin.pack(side=tk.RIGHT, padx=(10, 0))

        self.length_slider = ttk.Scale(
            length_frame,
            from_=4,
            to=64,
            orient="horizontal",
            variable=self.length_var,
            command=self.on_slider_change
        )
        self.length_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

        # Presets Buttons
        preset_frame = tk.Frame(settings_card, bg=CARD_BG)
        preset_frame.pack(fill=tk.X, pady=(0, 15))

        presets = [("PIN (4)", 4), ("Standard (12)", 12), ("Strong (16)", 16), ("Key (32)", 32)]
        for label, size in presets:
            btn = tk.Button(
                preset_frame,
                text=label,
                font=("Segoe UI", 8),
                bg="#f1f5f9",
                fg="#334155",
                bd=1,
                relief="groove",
                cursor="hand2",
                command=lambda s=size: self.set_preset_length(s)
            )
            btn.pack(side=tk.LEFT, me=5)

        # Checkboxes for Character Pools
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)

        cb_frame = tk.Frame(settings_card, bg=CARD_BG)
        cb_frame.pack(fill=tk.X)

        cbs = [
            ("Include Uppercase (A-Z)", self.uppercase_var),
            ("Include Lowercase (a-z)", self.lowercase_var),
            ("Include Digits (0-9)", self.digits_var),
            ("Include Symbols (!@#$...)", self.symbols_var),
            ("Exclude Ambiguous (i, l, 1, I, o, 0, O)", self.ambiguous_var),
        ]

        for text, var in cbs:
            cb = tk.Checkbutton(
                cb_frame,
                text=text,
                variable=var,
                font=("Segoe UI", 9.5),
                bg=CARD_BG,
                activebackground=CARD_BG,
                anchor="w",
                command=self.generate_password
            )
            cb.pack(fill=tk.X, pady=2)

        # Custom Exclude Chars
        exclude_frame = tk.Frame(settings_card, bg=CARD_BG)
        exclude_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Label(exclude_frame, text="Custom Exclude Chars:", font=("Segoe UI", 9), bg=CARD_BG, fg="#64748b").pack(side=tk.LEFT)
        self.custom_exclude_var = tk.StringVar()
        self.custom_exclude_var.trace_add("write", lambda *args: self.generate_password())
        
        exclude_entry = tk.Entry(exclude_frame, textvariable=self.custom_exclude_var, font=("Consolas", 9), width=15)
        exclude_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Generate Action Button
        gen_btn = tk.Button(
            main_frame,
            text="🔄 Generate New Password",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self.generate_password
        )
        gen_btn.pack(fill=tk.X, pady=(0, 15))

        # History Frame
        history_frame = tk.LabelFrame(
            main_frame,
            text=" Session History (Double-click to copy) ",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg="#475569",
            padx=10,
            pady=10
        )
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(
            history_frame,
            font=("Consolas", 10),
            bd=0,
            selectbackground="#e2e8f0",
            selectforeground="#0f172a",
            highlightthickness=0
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<Double-Button-1>", self.copy_selected_history)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

    def on_slider_change(self, val):
        self.length_var.set(int(float(val)))
        self.generate_password()

    def on_length_spin_change(self):
        self.generate_password()

    def set_preset_length(self, length: int):
        self.length_var.set(length)
        self.generate_password()

    def get_config() -> PasswordConfig:
        return PasswordConfig(
            length=self.length_var.get(),
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_digits=self.digits_var.get(),
            use_symbols=self.symbols_var.get(),
            exclude_ambiguous=self.ambiguous_var.get(),
            custom_exclude=self.custom_exclude_var.get()
        )

    def generate_password(self):
        config = PasswordConfig(
            length=self.length_var.get(),
            use_uppercase=self.uppercase_var.get(),
            use_lowercase=self.lowercase_var.get(),
            use_digits=self.digits_var.get(),
            use_symbols=self.symbols_var.get(),
            exclude_ambiguous=self.ambiguous_var.get(),
            custom_exclude=self.custom_exclude_var.get()
        )

        try:
            pwd = PasswordGenerator.generate(config)
            self.password_var.set(pwd)

            entropy = PasswordGenerator.calculate_entropy(pwd, config)
            strength, color_code, desc = PasswordGenerator.assess_strength(entropy)

            self.strength_label.config(text=f"Strength: {strength}", fg=color_code)
            self.entropy_label.config(text=f"{entropy:.1f} bits entropy")

            # Update strength bar
            total_width = self.meter_canvas.winfo_width() or 500
            ratio = min(entropy / 120.0, 1.0)
            fill_width = max(int(total_width * ratio), 10)
            self.meter_canvas.coords(self.meter_bar, 0, 0, fill_width, 8)
            self.meter_canvas.itemconfig(self.meter_bar, fill=color_code)

            # Add to history
            self.history_listbox.insert(0, pwd)
            if self.history_listbox.size() > 50:
                self.history_listbox.delete(50, tk.END)

        except ValueError as e:
            self.strength_label.config(text="Selection Error", fg="#ef4444")
            self.entropy_label.config(text="0 bits")
            self.meter_canvas.coords(self.meter_bar, 0, 0, 0, 8)
            self.password_var.set(f"Error: {e}")

    def copy_password(self):
        pwd = self.password_var.get()
        if pwd and not pwd.startswith("Error:"):
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Copied!", "Password copied to clipboard successfully.")

    def copy_selected_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            pwd = self.history_listbox.get(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Copied!", f"Copied from history:\n{pwd}")

def launch_gui():
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
