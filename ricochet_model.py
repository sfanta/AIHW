import sys

# Directions
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

class RicochetState:
    """
    Represents a snapshot of the board.
    robots: A tuple of (x, y) coordinates for all robots. 
            Standardize: robots[0] is usually the target robot.
    """
    def __init__(self, robots):
        self.robots = tuple(robots) # Tuple is hashable
        
    def __eq__(self, other):
        return self.robots == other.robots
    
    def __hash__(self):
        return hash(self.robots)
    
    def __repr__(self):
        return str(self.robots)

class RicochetEnvironment:
    def __init__(self, size, walls, goal_pos, target_robot_index=0):
        """
        size: int (e.g., 16 for a 16x16 grid)
        walls: set of ((x, y), direction) tuples indicating a wall is blocking 
               movement from (x,y) in that direction. 
               Alternatively, model walls as occupied squares or edges.
        goal_pos: (x, y)
        """
        self.size = size
        self.walls = walls # Logic depends on how you store walls (cells vs edges)
        self.goal_pos = goal_pos
        self.target_idx = target_robot_index

    def get_neighbors(self, state):
        """
        Generates valid child states.
        Logic: Pick every robot, try to slide it in every 4 directions.
        """
        neighbors = []
        current_positions = set(state.robots)

        for i, (rx, ry) in enumerate(state.robots):
            for dx, dy in DIRECTIONS:
                # Calculate the slide
                new_x, new_y = self._slide(rx, ry, dx, dy, current_positions)
                
                # If the robot actually moved
                if (new_x, new_y) != (rx, ry):
                    new_robots = list(state.robots)
                    new_robots[i] = (new_x, new_y)
                    
                    # Calculate cost (usually 1 move = cost 1)
                    cost = 1 
                    neighbors.append((RicochetState(new_robots), cost))
        
        return neighbors

    def _slide(self, x, y, dx, dy, all_robot_positions):
        """
        Moves from x,y in direction dx,dy until hitting a wall or robot.
        Returns the final coordinates.
        """
        cx, cy = x, y
        
        while True:
            nx, ny = cx + dx, cy + dy
            
            # 1. Check Board Boundaries
            if not (0 <= nx < self.size and 0 <= ny < self.size):
                return cx, cy
            
            # 2. Check Static Walls (Implementation depends on your wall data structure)
            # if self.is_wall_blocking(cx, cy, dx, dy): return cx, cy
            
            # 3. Check Other Robots
            if (nx, ny) in all_robot_positions:
                return cx, cy
            
            # If clear, advance
            cx, cy = nx, ny
            
        return cx, cy

    def is_goal(self, state):
        return state.robots[self.target_idx] == self.goal_pos