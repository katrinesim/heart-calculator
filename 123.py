import tkinter as tk
from tkinter import messagebox, ttk
import math
import re
from datetime import datetime

class HeartCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Heart Calculator Pro ❤️✨")
        self.root.geometry("480x780")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffebf2")

        self.current_input = tk.StringVar(value="0")
        self.history = []
        self.max_history_items = 20
        self.formula_mode = tk.StringVar(value="basic")

        self.setup_display()
        self.setup_formula_tabs()
        self.setup_history_panel()
        self.setup_enhanced_buttons()  # НОВЫЙ ЛAYOUT
        self.bind_keyboard()

    def setup_display(self):
        display_frame = tk.Frame(self.root, bg="#ffebf2", bd=3, relief="ridge")
        display_frame.pack(pady=15, padx=20, fill="x")

        self.history_label = tk.Label(
            display_frame, text="Last: —", font=("Arial", 10),
            bg="#ffd6e7", fg="#8b0000", anchor="e"
        )
        self.history_label.pack(fill="x", padx=15, pady=(0, 5))

        self.display = tk.Entry(
            display_frame, textvariable=self.current_input,
            font=("Arial", 22, "bold"), bg="#ffd6e7", fg="#8b0000",
            justify="right", bd=0, relief="flat", insertbackground="#8b0000"
        )
        self.display.pack(padx=15, pady=10, fill="x")

        self.formula_label = tk.Label(
            display_frame, text="Basic Mode", font=("Arial", 9),
            bg="#ffd6e7", fg="#666"
        )
        self.formula_label.pack(pady=(0, 5))

    def setup_formula_tabs(self):
        tab_frame = tk.Frame(self.root, bg="#ffebf2")
        tab_frame.pack(pady=5, padx=20, fill="x")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Formula.TNotebook', background="#ffebf2")
        style.configure('Formula.TNotebook.Tab', padding=[20, 8], font=('Arial', 10, 'bold'))

        self.notebook = ttk.Notebook(tab_frame, style='Formula.TNotebook')
        self.notebook.add(tk.Frame(self.notebook, bg="#ffebf2"), text="📐 Formulas")
        self.notebook.pack(fill="x")

    def setup_history_panel(self):
        history_frame = tk.Frame(self.root, bg="#ffebf2")
        history_frame.pack(pady=(0, 10), padx=20, fill="x")

        header_frame = tk.Frame(history_frame, bg="#ffebf2")
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="📜 History", font=("Arial", 12, "bold"),
                bg="#ffebf2", fg="#e91e63").pack(side="left")
        
        tk.Button(header_frame, text="🗑️ Clear", font=("Arial", 9, "bold"),
                 bg="#e91e63", fg="white", bd=2, command=self.clear_history).pack(side="right")

        hist_frame = tk.Frame(history_frame, bg="#fff0f5", bd=2, relief="groove")
        hist_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(hist_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_text = tk.Text(hist_frame, height=4, font=("Arial", 9),
                                  bg="#fff0f5", fg="#8b0000", state="disabled",
                                  yscrollcommand=scrollbar.set)
        self.history_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_text.yview)

        self.history_text.bind("<Double-1>", self.copy_history_to_input)

    def setup_enhanced_buttons(self):
        """🎨 НОВЫЙ УМНЫЙ ЛAYOUT - 5x6 сетка с логическими группами"""
        buttons_frame = tk.Frame(self.root, bg="#ffebf2")
        buttons_frame.pack(expand=True, fill="both", padx=20, pady=5)

        # 🎨 ЦВЕТОВАЯ СХЕМА:
        # Красный: Очистка/Удаление (#ff6b8b)
        # Розовый: Функции (#ff99cc)  
        # Фиолетовый: Операторы (#ff80ab)
        # Светло-розовый: Цифры (#ffc2d1)
        # Глубокий розовый: Равно (#e91e63)

        # 🗺️ ЛОГИЧЕСКАЯ РАССТАНОВКА:
        button_config = [
            # Строка 0: ОЧИСТКА | КОНСТАНТЫ
            [('AC', '#ff6b8b'), ('C', '#ff6b8b'), ('⌫', '#ff6b8b'), ('±', '#ff99cc'), ('%', '#ff99cc')],
            
            # Строка 1: ТРИГОНОМЕТРИЯ | ЛОГАРИФМЫ
            [('sin', '#ff99cc'), ('cos', '#ff99cc'), ('tan', '#ff99cc'), ('log', '#ff99cc'), ('ln', '#ff99cc')],
            
            # Строка 2: КОНСТАНТЫ | СТЕПЕНЬ/КОРЕНЬ
            [('π', '#ff99cc'), ('e', '#ff99cc'), ('√', '#ff99cc'), ('x²', '#ff99cc'), ('xʸ', '#ff99cc')],
            
            # Строка 3: 7 8 9 ДЕЛЕНИЕ
            [('7', '#ffc2d1'), ('8', '#ffc2d1'), ('9', '#ffc2d1'), ('÷', '#ff80ab'), ('1/x', '#ff99cc')],
            
            # Строка 4: 4 5 6 УМНОЖЕНИЕ
            [('4', '#ffc2d1'), ('5', '#ffc2d1'), ('6', '#ffc2d1'), ('×', '#ff80ab'), ('!', '#ff99cc')],
            
            # Строка 5: 1 2 3 ВЫЧИТАНИЕ
            [('1', '#ffc2d1'), ('2', '#ffc2d1'), ('3', '#ffc2d1'), ('−', '#ff80ab'), ('abs', '#ff99cc')],
            
            # Строка 6: 0 . РАВНО (широкое)
            [('0', '#ffc2d1', 2), ('.', '#ffc2d1'), ('+', '#ff80ab'), ('=', '#e91e63', 2)]
        ]

        for row, buttons in enumerate(button_config):
            for col, (text, color, *colspan) in enumerate(buttons):
                cs = colspan[0] if colspan else 1
                btn = self.create_heart_button(buttons_frame, text, color, row, col, cs)
                btn.grid(row=row, column=col, columnspan=cs, padx=5, pady=5, sticky="nsew")

        # Равномерное растягивание
        for i in range(7): buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(5): buttons_frame.grid_columnconfigure(i, weight=1)

    def create_heart_button(self, parent, text, color, row, col, colspan=1):
        """Сердце-кнопка с анимацией"""
        btn = tk.Button(
            parent, text=text, font=("Arial Rounded MT Bold", 13 if len(text)<4 else 11),
            bg=color, fg="white", bd=0, relief="flat", cursor="heart",
            height=2, width=6 if colspan==1 else 12,
            command=lambda t=text: self.button_click(t),
            activebackground=self.darken_color(color, 0.85)
        )
        
        # ✨ Анимация нажатия
        def animate_press(e):
            btn.config(relief="sunken", bd=2)
        def animate_release(e):
            btn.after(80, lambda: btn.config(relief="flat", bd=0))
            
        btn.bind("<Button-1>", animate_press)
        btn.bind("<ButtonRelease-1>", animate_release)
        btn.bind("<Enter>", lambda e: btn.config(bg=self.darken_color(color, 0.95)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        
        return btn

    def darken_color(self, color, factor=0.85):
        try:
            r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
            return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        except:
            return color

    # ========== ЛОГИКА КАЛЬКУЛЯТОРА (сокращено для примера) ==========
    
    def button_click(self, char):
        handlers = {
            'AC': self.clear_all, 'C': self.clear_entry, '⌫': self.backspace,
            '±': self.change_sign, '%': lambda: self.append('%'),
            'π': lambda: self.append('π'), 'e': lambda: self.append('e'),
            '=': self.calculate, '.': lambda: self.append('.')
        }
        handler = handlers.get(char, self.handle_function)
        handler(char)

    def handle_function(self, func):
        """Обработка математических функций"""
        current = self.current_input.get()
        functions = {
            'sin': f'sin({current})', 'cos': f'cos({current})', 'tan': f'tan({current})',
            'log': f'log({current})', 'ln': f'ln({current})',
            '√': f'√({current})', 'x²': f'{current}^2', 'xʸ': f'{current}^',
            '1/x': f'1/({current})', '!': f'factorial({current})',
            'abs': f'abs({current})'
        }
        if func in functions:
            self.current_input.set(functions[func])

    def change_sign(self):
        current = self.current_input.get()
        if current.startswith('-'):
            self.current_input.set(current[1:])
        else:
            self.current_input.set('-' + current)

    def append(self, char):
        current = self.current_input.get()
        if current == "0" and char not in 'πe.':
            self.current_input.set(char)
        else:
            self.current_input.set(current + char)

    def backspace(self):
        current = self.current_input.get()
        self.current_input.set(current[:-1] or "0")

    def clear_all(self):
        self.current_input.set("0")

    def clear_entry(self):
        self.current_input.set("0")

    def calculate(self):
        # Упрощённый расчёт (полная версия в предыдущих примерах)
        try:
            expr = self.current_input.get().replace('×','*').replace('÷','/').replace('^','**')
            expr = expr.replace('π', str(math.pi)).replace('e', str(math.e))
            result = eval(expr, {"__builtins__": {}, "math": math})
            result_str = f"{result:.10g}".rstrip('0').rstrip('.')
            self.current_input.set(result_str or "0")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.add_to_history(f"[{timestamp}] {self.current_input.get()} = {result_str}")
        except:
            messagebox.showerror("Error", "Calculation failed!")

    def add_to_history(self, entry):
        self.history.append(entry)
        if len(self.history) > self.max_history_items:
            self.history.pop(0)
        self.update_history_display()

    def update_history_display(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for item in reversed(self.history):
            self.history_text.insert(tk.END, item + "\n")
        self.history_text.config(state="disabled")

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all history?"):
            self.history = []
            self.update_history_display()

    def copy_history_to_input(self, event):
        try:
            selection = self.history_text.selection_get()
            expr = selection.split('=')[0].strip('[] ')
            self.current_input.set(expr)
        except:
            pass

    def bind_keyboard(self):
        self.root.bind('<Key>', self.key_press)
        self.root.focus_set()

    def key_press(self, event):
        key = event.char
        if key.isdigit() or key in '.+-*/πe':
            self.append(key)
        elif key == '\r':
            self.calculate()
        elif key == '\x08':
            self.backspace()

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartCalculator(root)
    root.mainloop()
