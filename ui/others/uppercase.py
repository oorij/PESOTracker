from PyQt5.QtWidgets import QLineEdit

class UpperCaseLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def keyPressEvent(self, event):
        # Modify the input character to uppercase if it's a letter
        text = event.text()
        if text.islower():
            event = type(event)(event.type(), event.key(), event.modifiers(), text.upper())
        super().keyPressEvent(event)