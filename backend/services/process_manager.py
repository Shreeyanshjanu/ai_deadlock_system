from typing import Dict, List
import time

class ProcessManager:
    def __init__(self):
        self.processes: Dict = {}
        self.process_counter = 0
    
    def create_process(self, name: str, resources: List[int] = None) -> int:
        self.process_counter += 1
        process_id = self.process_counter
        
        self.processes[process_id] = {
            "id": process_id,
            "name": name,
            "allocated": [],
            "requested": resources or [],
            "wait_time": 0,
            "created_at": time.time(),
            "state": "ready"
        }
        
        return process_id
    
    def terminate_process(self, process_id: int):
        if process_id in self.processes:
            del self.processes[process_id]
    
    def get_all_processes(self) -> List[Dict]:
        return list(self.processes.values())
    
    def reset(self):
        self.processes = {}
        self.process_counter = 0
