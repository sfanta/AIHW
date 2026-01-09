import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style for professional looking plots
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

INPUT_FILE = "experiment_results.csv"
OUTPUT_TIME_PLOT = "time_plot.png"
OUTPUT_NODES_PLOT = "nodes_plot.png"

def plot_experiments():
    # 1. Load Data
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}. Run experiments.py first.")
        return

    # 2. Data Cleaning
    # Convert 'TIMEOUT' to NaN so pandas can handle it (it won't plot them)
    # or you can set it to a high number to show it went off the chart.
    # Here we convert to numeric, coercing errors (TIMEOUT) to NaN.
    df['AStar_Time'] = pd.to_numeric(df['AStar_Time'], errors='coerce')
    df['PDDL_Time'] = pd.to_numeric(df['PDDL_Time'], errors='coerce')
    
    # Fill NaNs with a specific value if you want to show them as "maxed out"
    # or just drop them to show gaps. Let's keep them as NaN to break the line.
    
    # 3. Aggregation (Average over the 3 iterations per size)
    grouped = df.groupby('GridSize').mean()
    
    # ==========================================
    # PLOT 1: RUNTIME
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    # Plot A* Time
    plt.plot(grouped.index, grouped['AStar_Time'], marker='o', label='A* (Custom)', linewidth=2, markersize=8)
    
    # Plot PDDL Time
    plt.plot(grouped.index, grouped['PDDL_Time'], marker='s', label='PDDL (Fast Downward)', linewidth=2, markersize=8)
    
    plt.title('Average Runtime: A* vs PDDL', fontsize=16)
    plt.xlabel('Grid Size (NxN)', fontsize=14)
    plt.ylabel('Time (seconds)', fontsize=14)
    plt.legend()
    plt.yscale('log') # Log scale is often better if A* is super fast vs PDDL overhead
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_TIME_PLOT)
    print(f"Saved {OUTPUT_TIME_PLOT}")
    plt.close()

    # ==========================================
    # PLOT 2: NODES EXPANDED
    # ==========================================
    plt.figure(figsize=(10, 6))
    
    # Plot A* Expanded
    plt.plot(grouped.index, grouped['AStar_Expanded'], marker='o', label='A* Nodes', color='tab:blue', linewidth=2)
    
    # Plot PDDL Expanded
    plt.plot(grouped.index, grouped['PDDL_Expanded'], marker='s', label='PDDL Nodes', color='tab:orange', linewidth=2)
    
    plt.title('Search Space Explored: Nodes Expanded', fontsize=16)
    plt.xlabel('Grid Size (NxN)', fontsize=14)
    plt.ylabel('Number of Nodes (Log Scale)', fontsize=14)
    plt.yscale('log') # Crucial because A* expands WAY more
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_NODES_PLOT)
    print(f"Saved {OUTPUT_NODES_PLOT}")
    plt.close()

if __name__ == "__main__":
    plot_experiments()