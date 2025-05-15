from explorateur import Explorateur, ExplorationType, SearchType
import numpy as np
from lpsolver import LPInstance
import json
import sys
import time
from pathlib import Path
from state import State



# Branch and bound algorithm for solving integer programming problems
# Uses the linear programming relaxation of the integer programming problem
# as a lower bound for the search
class BranchAndBound:
    def __init__(self, filename: str) -> None:
        numT, numD, cst, A = data_parse(filename)
        self.lp_instance = LPInstance(numT, numD, cst, A)

        
    def objective_function(self, state):
        return state.get_objective()

    def solve(self, var_selection_strategy="weighted", exploration_type="best_first"):
        # Reset class variables before starting a new search
        State._lp_instance = None
        State._best_objective = float("inf")
        State._best_solution = None
        State._best_fixed_vars = None
        State._found_solution = False
        
        # Debug
        explorer = Explorateur(is_verbose=False) 

        # Root node
        initial_state = State(
            self.lp_instance, var_selection_strategy=var_selection_strategy
        )

        # Search type
        exp_type = ExplorationType.DepthFirst()
        
        # Run search
        print(
            f"Starting Explorateur search with {exploration_type} strategy and {var_selection_strategy} variable selection"
        )

        found_solution = explorer.search(
            initial_state,
            exploration_type=exp_type,
            search_type=SearchType.GraphSearch(),  
            is_solution_path=False,             
            max_depth=100000,                     
            max_moves=1000000,                    
            dot_filename="output.dot",
        )

        print(f"Explorateur processed {explorer.num_decisions} nodes.")
        
        if State._found_solution:
            print(f"Best objective: {State._best_objective}")
            return round(State._best_objective)
        else:
            print("No solution found.")
            return float("inf")

def data_parse(filename: str):
    try:
        with open(filename, "r") as fl:
            numTests = int(fl.readline().strip())  # n
            numDiseases = int(fl.readline().strip())  # m

            costOfTest = np.array([float(i) for i in fl.readline().strip().split()])

            A = np.zeros((numTests, numDiseases))
            for i in range(0, numTests):
                A[i, :] = np.array([int(i) for i in fl.readline().strip().split()])
            return numTests, numDiseases, costOfTest, A
    except Exception as e:
        print(f"Error reading instance file. File format may be incorrect.{e}")
        exit(1)


# Main function
def main(filepath: str):
    filename = Path(filepath).name
    
    print(f"Solving {filename}")
    
   
    start_time = time.time()

    solver = BranchAndBound(filepath)
    print(solver.lp_instance.model.export_as_lp_string())
    solver.lp_instance.model.solve()

    best_cost = solver.solve()
    end_time = time.time()

    total_time = "{:.2f}".format(end_time - start_time)
    best_cost = round(best_cost) if best_cost != float("inf") else "--"

    sol_dict = {
        "Instance": filename,
        "Time": total_time,
        "Result": best_cost,
        "Solution": "OPT" if best_cost != float("inf") else "--"
    }
    print(json.dumps(sol_dict))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file> ")
        sys.exit(1)
        
    filepath = sys.argv[1]
    
    main(filepath)