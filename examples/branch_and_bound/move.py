from explorateur import BaseMove

class Move(BaseMove):
    def __init__(self, var_index, value):
        self.var_index = var_index
        self.value = value

    def __str__(self) -> str:
        return f"Set x_{self.var_index} = {self.value}"

    def get_dot_label(self) -> str:
        return f"x_{self.var_index}={self.value}"