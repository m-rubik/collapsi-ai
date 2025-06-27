class Card:
    def __init__(self, value):
        self.value = value
        self.collapsed = False

    def __repr__(self):
        return f"{self.value[0]}{'x ' if self.collapsed else '  '}"