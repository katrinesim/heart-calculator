import tkinter as tk
from tkinter import messagebox
import math
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import operator

class HeartCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("HeartCalculator Pro ❤️✨")
        self.root.geometry("480x780")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffebf2")

        self.current_input = tk.StringVar(value="0")
        self.history = []
        self.max_history_items = 50
        self.pending_operation = None
        self.last_result = 0.0
        self.decimal_used = False
        self.expression_stack = []

        self.setup_display()
        self.setup_history_panel()
        self.setup_enhanced_buttons()
        self.bind_keyboard()
        self.root.focus_set()

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
            justify="right", bd=0, relief="flat", insertbackground="#8b0000",
            state="readonly"
        )
        self.display.pack(padx=15, pady=10, fill="x")

        self.formula_label = tk.Label(
            display_frame, text="Basic Mode", font=("Arial", 9),
            bg="#ffd6e7", fg="#666"
        )
        self.formula_label.pack(pady=(0, 5))

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
                                  yscrollcommand=scrollbar.set, wrap="word")
        self.history_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_text.yview)

        self.history_text.bind("<Double-1>", self.copy_history_to_input)
        self.history_text.bind("<Button-3>", self.show_history_context_menu)

    def setup_enhanced_buttons(self):
        buttons_frame = tk.Frame(self.root, bg="#ffebf2")
        buttons_frame.pack(expand=True, fill="both", padx=20, pady=5)

        button_config = [
            [('AC', '#ff6b8b'), ('C', '#ff6b8b'), ('⌫', '#ff6b8b'), ('±', '#ff99cc'), ('%', '#ff99cc')],
            [('sin', '#ff99cc'), ('cos', '#ff99cc'), ('tan', '#ff99cc'), ('log', '#ff99cc'), ('ln', '#ff99cc')],
            [('π', '#ff99cc'), ('e', '#ff99cc'), ('√', '#ff99cc'), ('x²', '#ff99cc'), ('xʸ', '#ff99cc')],
            [('7', '#ffc2d1'), ('8', '#ffc2d1'), ('9', '#ffc2d1'), ('÷', '#ff80ab'), ('1/x', '#ff99cc')],
            [('4', '#ffc2d1'), ('5', '#ffc2d1'), ('6', '#ffc2d1'), ('×', '#ff80ab'), ('!', '#ff99cc')],
            [('1', '#ffc2d1'), ('2', '#ffc2d1'), ('3', '#ffc2d1'), ('−', '#ff80ab'), ('abs', '#ff99cc')],
            [('0', '#ffc2d1', 2), ('.', '#ffc2d1'), ('+', '#ff80ab'), ('=', '#e91e63', 2)]
        ]

        for row, buttons in enumerate(button_config):
            for col, (text, color, *colspan) in enumerate(buttons):
                cs = colspan[0] if colspan else 1
                btn = self.create_heart_button(buttons_frame, text, color, row, col, cs)
                btn.grid(row=row, column=col, columnspan=cs, padx=5, pady=5, sticky="nsew")

        for i in range(7): buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(5): buttons_frame.grid_columnconfigure(i, weight=1)

    def create_heart_button(self, parent, text, color, row, col, colspan=1):
        btn = tk.Button(
            parent, text=text, font=("Arial Rounded MT Bold", 13 if len(text)<4 else 11),
            bg=color, fg="white", bd=0, relief="flat", cursor="hand2",
            height=2, width=6 if colspan==1 else 12,
            command=lambda t=text: self.button_click(t),
            activebackground=self.darken_color(color, 0.85)
        )
        
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
            color = color.lstrip('#')
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        except:
            return color

    # ========== ENHANCED CALCULATION ENGINE ==========
    
    def button_click(self, char):
        try:
            if char.isdigit():
                self.append_digit(char)
            elif char in '+-×÷':
                self.handle_operator(char)
            elif char == '=':
                self.calculate()
            elif char == 'AC':
                self.clear_all()
            elif char == 'C':
                self.clear_entry()
            elif char == '⌫':
                self.backspace()
            elif char == '±':
                self.change_sign()
            elif char == '.':
                self.append_decimal()
            elif char in ('π', 'e'):
                self.append_constant(char)
            else:
                self.handle_function(char)
        except Exception as e:
            self.show_error("Button error")

    def safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float with error handling"""
        try:
            return float(value)
        except ValueError:
            return None

    def append_digit(self, digit: str):
        current = self.current_input.get()
        if current == "0" and digit != "0":
            self.current_input.set(digit)
        else:
            self.current_input.set(current + digit)

    def append_decimal(self):
        current = self.current_input.get()
        if '.' not in current:
            self.current_input.set(current + '.')

    def append_constant(self, const: str):
        const_map = {'π': str(math.pi), 'e': str(math.e)}
        self.current_input.set(const_map.get(const, const))

    def handle_operator(self, op: str):
        try:
            current = self.safe_float(self.current_input.get())
            if current is not None:
                if self.pending_operation:
                    self.last_result = self.execute_operation(self.last_result, current, self.pending_operation)
                    self.current_input.set(self.format_result(self.last_result))
                
                self.pending_operation = self.map_operator(op)
                self.update_history_label(f"{self.format_result(self.last_result)} {op}")
        except Exception:
            pass

    def map_operator(self, op: str) -> callable:
        op_map = {
            '+': operator.add,
            '−': operator.sub,
            '×': operator.mul,
            '÷': operator.truediv
        }
        return op_map.get(op, operator.add)

    def execute_operation(self, a: float, b: float, operation: callable) -> float:
        try:
            if operation == operator.truediv and abs(b) < 1e-10:
                raise ZeroDivisionError("Division by zero")
            return operation(a, b)
        except ZeroDivisionError:
            self.show_error("Cannot divide by zero")
            return b

    def handle_function(self, func: str):
        try:
            current = self.safe_float(self.current_input.get())
            if current is None:
                return

            func_map = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log10,
                'ln': math.log,
                '√': lambda x: math.sqrt(abs(x)),
                'x²': lambda x: x * x,
                '1/x': lambda x: 1/x if abs(x) > 1e-10 else float('inf'),
                'abs': abs,
                '%': lambda x: x / 100
            }
            
            if func == '!':
                result = self.factorial(int(abs(current)))
            elif func == 'xʸ':
                self.current_input.set(f"{current}**")
                return
            else:
                func_impl = func_map.get(func)
                if func_impl:
                    result = func_impl(current)
                else:
                    return

            self.current_input.set(self.format_result(result))
            self.last_result = result

        except Exception as e:
            self.show_error(f"Function error: {str(e)[:30]}")

    def factorial(self, n: int) -> float:
        if n < 0:
            raise ValueError("Factorial undefined for negative numbers")
        if n > 170:
            raise ValueError("Result too large")
        result = 1.0
        for i in range(2, n + 1):
            result *= i
        return result

    def calculate(self):
        try:
            current = self.safe_float(self.current_input.get())
            if current is not None and self.pending_operation:
                result = self.execute_operation(self.last_result, current, self.pending_operation)
                self.current_input.set(self.format_result(result))
                self.last_result = result
                self.pending_operation = None
                self.add_to_history(f"{self.format_result(self.last_result)}")
            self.update_history_label("—")
        except Exception:
            self.show_error("Calculation failed")

    def format_result(self, value: float) -> str:
        """Format float with intelligent precision"""
        if math.isinf(value):
            return "∞"
        if math.isnan(value):
            return "NaN"
        
        # Use scientific notation for very large/small numbers
        if abs(value) > 1e12 or (0 < abs(value) < 1e-12):
            return f"{value:.8g}"
        
        # Regular formatting
        result = f"{value:.12g}".rstrip('0').rstrip('.')
        return result if result else "0"

    def change_sign(self):
        current = self.current_input.get()
        if current == "0" or current == "-0":
            return
        if current.startswith('-'):
            self.current_input.set(current[1:])
        else:
            self.current_input.set('-' + current)

    def backspace(self):
        current = self.current_input.get()
        if len(current) > 1:
            self.current_input.set(current[:-1])
        else:
            self.current_input.set("0")

    def clear_all(self):
        self.current_input.set("0")
        self.history = []
        self.pending_operation = None
        self.last_result = 0.0
        self.decimal_used = False
        self.expression_stack = []
        self.update_history_label("—")
        self.update_history_display()

    def clear_entry(self):
        self.current_input.set("0")
        self.pending_operation = None
        self.decimal_used = False

    def update_history_label(self, text: str):
        self.history_label.config(text=f"Last: {text}")

    def add_to_history(self, entry: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_entry = f"[{timestamp}] {entry}"
        self.history.append(full_entry)
        if len(self.history) > self.max_history_items:
            self.history.pop(0)
        self.update_history_display()

    def update_history_display(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for item in reversed(self.history[-10:]):  # Show last 10 items
            self.history_text.insert(tk.END, item + "\n")
        self.history_text.config(state="disabled")
        self.history_text.see(tk.END)

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all history?"):
            self.history = []
            self.update_history_display()

    def copy_history_to_input(self, event):
        try:
            selection = self.history_text.selection_get()
            if selection:
                # Extract expression before '='
                expr = re.split(r'\s*=\s*', selection.strip())[0]
                expr = re.sub(r'^\$\d{2}:\d{2}:\d{2}\$\s*', '', expr).strip()
                self.current_input.set(expr or "0")
        except tk.TclError:
            pass

    def show_history_context_menu(self, event):
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Copy", command=lambda: self.history_text.event_generate("<<Copy>>"))
            menu.add_command(label="Clear History", command=self.clear_history)
            menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def show_error(self, message: str):
        self.current_input.set("Error")
        messagebox.showerror("Error", message)

    def bind_keyboard(self):
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<Return>', lambda e: self.calculate())
        self.root.bind('<KP_Enter>', lambda e: self.calculate())
        self.root.bind('<BackSpace>', lambda e: self.backspace())
        self.root.bind('<Escape>', lambda e: self.clear_entry())

    def key_press(self, event):
        key = event.char
        try:
            if key.isdigit():
                self.append_digit(key)
            elif key in '+-*/.':
                if key == '*': self.button_click('×')
                elif key == '/': self.button_click('÷')
                elif key == '.': self.append_decimal()
                else: self.button_click(key)
            elif key == '\t':  # Tab for π
                self.append_constant('π')
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartCalculator(root)
    root.mainloop()
