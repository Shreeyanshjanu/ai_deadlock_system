import networkx as nx
from typing import Dict, List, Tuple

class DeadlockDetector:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def detect_deadlock(self, processes: Dict, resources: Dict) -> Dict:
        """
        Detect deadlock using Resource Allocation Graph (RAG)
        """
        self.graph.clear()
        
        # Build RAG
        for proc_id, proc_data in processes.items():
            self.graph.add_node(f"P{proc_id}", type="process")
            
            # Add edges for allocated resources
            for res_id in proc_data.get("allocated", []):
                self.graph.add_node(f"R{res_id}", type="resource")
                self.graph.add_edge(f"R{res_id}", f"P{proc_id}")
            
            # Add edges for requested resources
            for res_id in proc_data.get("requested", []):
                self.graph.add_node(f"R{res_id}", type="resource")
                self.graph.add_edge(f"P{proc_id}", f"R{res_id}")
        
        # Detect cycle using DFS
        try:
            cycle = nx.find_cycle(self.graph)
            return {
                "has_deadlock": True,
                "cycle": [node for node, _ in cycle]
            }
        except nx.NetworkXNoCycle:
            return {"has_deadlock": False}
    
    def get_graph_data(self) -> Dict:
        """
        Return graph data for visualization
        """
        nodes = []
        edges = []
        
        for node in self.graph.nodes():
            nodes.append({
                "id": node,
                "type": self.graph.nodes[node].get("type", "unknown")
            })
        
        for edge in self.graph.edges():
            edges.append({
                "source": edge[0],
                "target": edge[1]
            })
        
        return {"nodes": nodes, "edges": edges}
