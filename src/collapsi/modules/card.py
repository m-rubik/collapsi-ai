class Card:
    def __init__(self, value, collapsed=False):
        self.value = value
        self.collapsed = collapsed

    def __repr__(self):
        return f"{self.value[0]}{'x ' if self.collapsed else '  '}"