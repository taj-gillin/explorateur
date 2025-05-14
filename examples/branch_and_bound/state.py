from explorateur import BaseState
import numpy as np

from move import Move

class State(BaseState):
    _lp_instance = None
    _best_objective = float("inf")
    _best_solution = None
    _best_fixed_vars = None
    _integer_tolerance = 1e-5 # For integer solution detection
    _found_solution = False

    def __init__(
        self,
        lp_instance,
        fixed_vars=None,
        var_selection_strategy="weighted",
    ):
        super().__init__()
        if State._lp_instance is None:
            State._lp_instance = lp_instance
        
        self.fixed_vars = dict(fixed_vars) if fixed_vars else {}
        self.var_selection_strategy = var_selection_strategy
        
        # Solve LP
        self.objective, self.solution = State._lp_instance.solve(
            fixed_vars=self.fixed_vars
        )

        # Update best solution if needed
        if self.solution is not None and self.is_integer_solution() and self.objective < State._best_objective:
            State._best_objective = self.objective
            State._best_solution = np.copy(self.solution)
            State._best_fixed_vars = dict(self.fixed_vars)
            State._found_solution = True
            
    def __lt__(self, other):
        """For BestFirst search: compare states based on objective value (lower is better)"""
        if self.solution is None:
            return False
        if other.solution is None:
            return True
        
        return self.objective < other.objective

    def is_integer_solution(self):
        """Check if the solution is integer"""
        if self.solution is None:
            return False
        return not np.any((self.solution > self._integer_tolerance) & 
                         (self.solution < 1.0 - self._integer_tolerance))

    def is_terminate(self, goal_state=None) -> bool:
        # NEVER TERMINATE because we are looking for absolute optimal solution
        # We never terminate, we need to explore everything (implicity or explicitly)
        return False

    def get_moves(self) -> list[Move]:
        # Prune
        if self.solution is None or self.objective >= State._best_objective - 1e-6:
            return []

        # Find fractional variables
        fractional_indices = np.where(
            (self.solution > self._integer_tolerance) & 
            (self.solution < 1.0 - self._integer_tolerance)
        )[0]
        
        # Integer solution
        if len(fractional_indices) == 0:
            return []

        # Choose variable to branch on
        branch_var = self.select_branching_variable(fractional_indices)

        # Create and return moves
        if self.solution[branch_var] > 0.5:
            return [Move(branch_var, 1), Move(branch_var, 0)]
        else:
            return [Move(branch_var, 0), Move(branch_var, 1)]

    def select_branching_variable(self, fractional_indices):
        if self.var_selection_strategy == "first":
            return fractional_indices[0]

        elif self.var_selection_strategy == "most_fractional":
            distances = np.abs(self.solution[fractional_indices] - 0.5)
            return fractional_indices[np.argmin(distances)]

        elif self.var_selection_strategy == "weighted":
            weights = State._lp_instance.costOfTest[fractional_indices]
            return fractional_indices[np.argmax(weights)]

    def execute(self, move: Move) -> bool:
        # Copy variables
        new_fixed_vars = dict(self.fixed_vars)
        new_fixed_vars[move.var_index] = move.value
        
        # Update fixed variables
        self.fixed_vars = new_fixed_vars
        
        # Solve LP
        self.objective, self.solution = State._lp_instance.solve(
            fixed_vars=self.fixed_vars, 
            initial_solution=self.solution
        )
        
        # Update best solution if needed
        if self.solution is not None and self.is_integer_solution() and self.objective < State._best_objective:
            State._best_objective = self.objective
            State._best_solution = np.copy(self.solution)
            State._best_fixed_vars = dict(self.fixed_vars)
            State._found_solution = True
            
        return self.solution is not None

    def get_objective(self) -> float:
        return self.objective if self.solution is not None else float("inf")

    def __str__(self) -> str:
        return f"Obj:{self.objective:.2f}, Fixed:{len(self.fixed_vars)}"
    
    def get_dot_label(self) -> str:
        return f"Obj:{self.objective:.2f}"

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.fixed_vars == other.fixed_vars

    def __hash__(self):
        return hash(frozenset(self.fixed_vars.items()))