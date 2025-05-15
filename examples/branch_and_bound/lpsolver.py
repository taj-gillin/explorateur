import numpy as np
from docplex.mp.model import Model
import numpy.typing as npt
from typing import Union


# Solves the linear programming relaxation of the integer programming problem
# Used for the lower bound of our algorithm
class LPInstance:
    def __init__(self, numT: int, numD: int, cst: np.ndarray, A: np.ndarray) -> None:
        self.numTests = numT
        self.numDiseases = numD
        self.costOfTest = cst
        self.A = A
        self.model = Model(name="LPInstance")  # CPLEX solver
        self.model.context.cplex_parameters.threads = 1

        self.create_variables()
        self.create_constraints()
        self.create_objective()

        print(self.solve())

    def create_variables(self):
        # Helper matrix
        # D[t, i, j] = 1 if test t can differentiate between disease i and j, 0 otherwise
        D = np.zeros((self.numTests, self.numDiseases, self.numDiseases))

        for t in range(self.numTests):
            for i in range(self.numDiseases):
                for j in range(i + 1, self.numDiseases):
                    if self.A[t, i] != self.A[t, j]:
                        D[t, i, j] = 1
        self.D = D

        # Variables
        # T[i] = 1 if test i is used, 0 otherwise
        T = self.model.continuous_var_list(self.numTests, name="T", lb=0, ub=1)

        self.T = T

    def create_constraints(self):
        # We must be able to differentiate between all diseases (disease pairs)
        for i in range(self.numDiseases):
            for j in range(i + 1, self.numDiseases):
                self.model.add_constraint(
                    self.model.sum(
                        self.T[t] * self.D[t, i, j] for t in range(self.numTests)
                    )
                    >= 1,
                    ctname=f"Disease {i} and {j} must be differentiated",
                )

    def create_objective(self):
        # Minimize the cost of the tests
        self.model.minimize(
            self.model.sum(self.costOfTest[t] * self.T[t] for t in range(self.numTests))
        )

    def toString(self):
        out = ""
        out = f"Number of test: {self.numTests}\n"
        out += f"Number of diseases: {self.numDiseases}\n"
        cst_str = " ".join([str(i) for i in self.costOfTest])
        out += f"Cost of tests: {cst_str}\n"
        A_str = "\n".join(
            [" ".join([str(j) for j in self.A[i]]) for i in range(0, self.A.shape[0])]
        )
        out += f"A:\n{A_str}"
        return out

    def solve(
        self,
        fixed_vars: Union[dict[int, int], None] = None,
    ) -> tuple[
        float,  # objective value
        Union[npt.NDArray[np.float64], None],  # solution vector
    ]:
        
        # Bound variables already fixed
        # An alternative approach would be to add additional constraints for
        # each fixed variable, but this solves faster
        original_bounds = {}
        if fixed_vars:
            for var_index, value in fixed_vars.items():
                original_bounds[var_index] = (
                    self.T[var_index].lb,
                    self.T[var_index].ub,
                )

                self.T[var_index].lb = value
                self.T[var_index].ub = value

        solution = self.model.solve()

        objective_value = float("inf")
        solution_vector = None

        solve_details = self.model.solve_details

        if solution:
            solve_status_string = solve_details.status
            # This is to check if we actually found a solution
            # Not ideal, but best we can do with CPLEX
            if solve_status_string in [
                "optimal",
                "integer optimal solution",
                "integer optimal, tolerance",
                "feasible",
                "integer feasible solution",
                "integer feasible, tolerance",
            ]:
                objective_value = solution.get_objective_value()
                solution_vector = np.array(solution.get_value_list(self.T))

        # Restore original bounds
        if original_bounds:
            for var_index, (lb, ub) in original_bounds.items():
                self.T[var_index].lb = lb
                self.T[var_index].ub = ub

        return objective_value, solution_vector
