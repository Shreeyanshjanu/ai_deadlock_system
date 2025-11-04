def dfs_cycle_detection(graph: dict) -> list:
    """
    Detect cycle in directed graph using DFS
    """
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Cycle detected
                cycle_start = path.index(neighbor)
                return path[cycle_start:]
        
        rec_stack.remove(node)
        path.pop()
        return False
    
    for node in graph:
        if node not in visited:
            result = dfs(node)
            if result:
                return result
    
    return []
