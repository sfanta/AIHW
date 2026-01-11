# Ricochet Robots AI Solver

This repository contains an Artificial Intelligence project that solves the **Ricochet Robots** puzzle using two distinct approaches:
1.  **Custom A* Search:** A Python implementation using the Manhattan Distance heuristic.
2.  **Automated Planning (PDDL):** A modeling approach using the **Fast Downward** planner to handle the complex sliding mechanics.

This project was developed for the **Artificial Intelligence** course (Autumn Term 2025-26) at Sapienza University of Rome.

## 📂 Project Structure

* `ricochet_model.py`: The environment logic (state representation, sliding transition function).
* `astar_solver.py`: Custom implementation of the A* algorithm (Task 2.1).
* `domain.pddl`: The PDDL domain file defining the "sliding physics" logic.
* `pddl_generator.py`: Script to dynamically generate PDDL problem files from Python states.
* `main.py`: Main driver script to run a single demo instance (Task 2.2).
* `experiments.py`: Benchmark script to run experiments on grid sizes 5x5 to 10x10 (Task 3).
* `plot_results.py`: Generates performance graphs from experiment data.
* `visualize.py`: Animated visualizer for the PDDL solution.

## 🛠️ Prerequisites

To run this project, you need the following:

1.  **Python 3.8+**
2.  **Fast Downward Planner** (Required for the PDDL solver)

### Python Dependencies
Install the required Python libraries:
```bash
pip install matplotlib pandas seaborn numpy
