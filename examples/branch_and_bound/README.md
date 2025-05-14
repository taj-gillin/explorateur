# Branch and Bound

This is a implementation of the Branch and Bound algorithm using `explorateur` and `docplex` to solve a Brown University's CSCI29510 Project 4. The goal is to find the minimum cost of tests to detect all diseases, given a set of tests, which diseases they test positive for, and the cost of each test.

## Installation

### Create virtual environment
```uv venv venv --python 3.9
source venv/bin/activate
uv pip install -r requirements.txt
``

### Install cplex

Download the cplex solver from [here](https://www.ibm.com/analytics/cplex-optimizer)

Export the cplex solver path
```export CP_SOLVER_EXEC=/Applications/CPLEX_Studio2211/cpoptimizer/bin/x86-64_osx/cpoptimizer
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/Applications/CPLEX_Studio2211/cpoptimizer/bin/x86-64_osx:/Applications/CPLEX_Studio2211/cplex/bin/x86-64_osx
export DOCPLEX_COS_LOCATION=/Applications/CPLEX_Studio2211
```

## Usage
```python main.py <input_file>```


