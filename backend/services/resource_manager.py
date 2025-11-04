from typing import Dict, List

class ResourceManager:
    def __init__(self):
        self.resources: Dict = {}
        self.resource_counter = 0
    
    def create_resource(self, name: str, instances: int = 1) -> int:
        self.resource_counter += 1
        resource_id = self.resource_counter
        
        self.resources[resource_id] = {
            "id": resource_id,
            "name": name,
            "instances": instances,
            "available": instances,
            "allocated_to": []
        }
        
        return resource_id
    
    def allocate_resource(self, process_id: int, resource_id: int) -> bool:
        if resource_id not in self.resources:
            return False
        
        resource = self.resources[resource_id]
        
        if resource["available"] > 0:
            resource["available"] -= 1
            resource["allocated_to"].append(process_id)
            return True
        
        return False
    
    def release_resource(self, process_id: int, resource_id: int):
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            if process_id in resource["allocated_to"]:
                resource["allocated_to"].remove(process_id)
                resource["available"] += 1
    
    def get_all_resources(self) -> List[Dict]:
        return list(self.resources.values())
    
    def reset(self):
        self.resources = {}
        self.resource_counter = 0
