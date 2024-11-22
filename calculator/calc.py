import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1, width=None, height=None):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text
        self.width = width
        self.height = height


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1, width=None, height=None):
        CalcButton.__init__(self, text, button_clicked, expand, width, height)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked, width=None, height=None):
        CalcButton.__init__(self, text, button_clicked, width=width, height=height)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked, width=None, height=None):
        CalcButton.__init__(self, text, button_clicked, width=width, height=height)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK


class CalculatorApp(ft.Container):
    # application's root control (i.e. "view") containing all other controls
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=30)
        self.width = 600
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ActionButton(text="x^2", button_clicked=self.button_clicked, width=20, height=50),
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked, width=20, height=50),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked, width=20, height=50),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked, width=20, height=50),
                        ActionButton(text="/", button_clicked=self.button_clicked, width=20, height=50),
                        
                    ]
                ),
                ft.Row(
                    controls=[
                        ActionButton(text="x^y"    , button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="7", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="8", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="9", button_clicked=self.button_clicked, width=20, height=50),
                        ActionButton(text="*", button_clicked=self.button_clicked, width=20, height=50),
                        
                    ]
                ),
                ft.Row(
                    controls=[
                        ActionButton(text="10^x", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="4", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="5", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="6", button_clicked=self.button_clicked, width=20, height=50),
                        ActionButton(text="-", button_clicked=self.button_clicked, width=20, height=50),
                        
                    ]
                ),
                ft.Row(
                    controls=[
                        ActionButton(text="x!", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="1", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="2", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="3", button_clicked=self.button_clicked, width=20, height=50),
                        ActionButton(text="+", button_clicked=self.button_clicked, width=20, height=50),
                        
                    ]
                ),
                ft.Row(
                    controls=[
                        ActionButton(text="π", button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked, width=20, height=50),
                        DigitButton(text=".", button_clicked=self.button_clicked, width=20, height=50),
                        ActionButton(text="=", button_clicked=self.button_clicked, width=20, height=50),
                        
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()

        elif data in ("%"):
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)

            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )
        elif data in ("x^2"):
            self.result.value = self.format_number(float(self.result.value) ** 2)

        elif data in ("x^y"):
            self.operand1 = float(self.result.value)
            self.operator = "^"
            self.new_operand = True

        elif data in ("10^x"):
            self.result.value = self.format_number(10 ** float(self.result.value))
            self.reset()

        elif data in ("x!"):
            if float(self.result.value) < 0:
                self.result.value = "Error"
            else:
                self.result.value = math.factorial(int(float(self.result.value)))
            self.reset()

        elif data in ("π"):
            self.result.value = self.format_number(3.141592653589793)

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):

        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
            
        elif operator == "^":
            return self.format_number(operand1 ** operand2)
        
        elif operator == "π":
            return self.format_number(operand1 * 3.141592653589793)
        
        else:
            return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Calc App"
    # create application instance
    calc = CalculatorApp()

    # add application's root control to the page
    page.add(calc)


ft.app(target=main)
