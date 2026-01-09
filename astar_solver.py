import heapq
import time

class AStarNode:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g = g # Cost from start
        self.h = h # Heuristic cost to goal
        self.f = g + h

    # For priority queue comparison
    def __lt__(self, other):
        return self.f < other.f

class AStarSolver:
    def __init__(self, env, heuristic_func):
        self.env = env
        self.heuristic = heuristic_func
        
        # Metrics [cite: 88, 90]
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_memory = 0
        
    def solve(self, start_state):
        start_time = time.time()
        
        # Open list (Priority Queue)
        open_list = []
        start_node = AStarNode(start_state, g=0, h=self.heuristic(start_state, self.env))
        heapq.heappush(open_list, start_node)
        
        # Closed set for "duplicate elimination and no reopening" 
        # We store states we have already Expanded (or visited)
        closed_set = set()
        
        # To handle duplicate detection in Open List effectively without reopening,
        # we can track best g-values seen so far.
        g_score = {start_state: 0}

        while open_list:
            # Update max memory metric [cite: 92]
            self.max_memory = max(self.max_memory, len(open_list) + len(closed_set))
            
            # Pop node with lowest f
            current_node = heapq.heappop(open_list)
            
            if current_node.state in closed_set:
                continue
            
            # Goal Check
            if self.env.is_goal(current_node.state):
                return self._reconstruct_path(current_node, start_time)
            
            # Add to closed set (Explored)
            closed_set.add(current_node.state)
            self.nodes_expanded += 1
            
            # Expand
            for neighbor_state, cost in self.env.get_neighbors(current_node.state):
                tentative_g = current_node.g + cost
                
                # Check if we found a better path or if it's new
                # Note: "No reopening" usually implies if it's in closed, we ignore it.
                if neighbor_state in closed_set:
                    continue
                
                if neighbor_state not in g_score or tentative_g < g_score[neighbor_state]:
                    g_score[neighbor_state] = tentative_g
                    h_val = self.heuristic(neighbor_state, self.env)
                    new_node = AStarNode(neighbor_state, current_node, tentative_g, h_val)
                    heapq.heappush(open_list, new_node)
                    self.nodes_generated += 1
                    
        return None # Failure

    def _reconstruct_path(self, node, start_time):
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return {
            "path": path[::-1],
            "time": time.time() - start_time,
            "expanded": self.nodes_expanded,
            "generated": self.nodes_generated,
            "memory": self.max_memory
        }