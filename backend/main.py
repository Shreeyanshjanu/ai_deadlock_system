from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import asyncio
import json
from models.deadlock_detector import DeadlockDetector
from models.ai_predictor import AIPredictor
from services.process_manager import ProcessManager
from services.resource_manager import ResourceManager

app = FastAPI(title="AI Deadlock Detection System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
detector = DeadlockDetector()
predictor = AIPredictor()
process_manager = ProcessManager()
resource_manager = ResourceManager()

# WebSocket connections
active_connections: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Send real-time updates - ADD AWAIT HERE!
            system_state = get_system_state()  # This should NOT be async
            await websocket.send_json(system_state)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/")
async def root():
    return {"message": "AI Deadlock Detection System API"}


@app.post("/api/process/create")
async def create_process(process_data: Dict):
    process_id = process_manager.create_process(
        process_data["name"],
        process_data.get("resources", [])
    )
    return {"process_id": process_id, "status": "created"}


@app.post("/api/resource/create")
async def create_resource(resource_data: Dict):
    resource_id = resource_manager.create_resource(
        resource_data["name"],
        resource_data.get("instances", 1)
    )
    return {"resource_id": resource_id, "status": "created"}


@app.post("/api/process/request")
async def request_resource(request_data: Dict):
    process_id = request_data["process_id"]
    resource_id = request_data["resource_id"]

    # Check for potential deadlock before allocation
    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    if prediction["deadlock_probability"] > 0.7:
        return {
            "status": "blocked",
            "reason": "High deadlock probability",
            "probability": prediction["deadlock_probability"]
        }

    success = resource_manager.allocate_resource(process_id, resource_id)

    # Detect actual deadlock
    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    if deadlock_info["has_deadlock"]:
        # Trigger resolution
        await resolve_deadlock(deadlock_info)

    return {
        "status": "allocated" if success else "failed",
        "deadlock_detected": deadlock_info["has_deadlock"]
    }


@app.post("/api/process/release")
async def release_resource(release_data: Dict):
    process_id = release_data["process_id"]
    resource_id = release_data["resource_id"]

    resource_manager.release_resource(process_id, resource_id)
    return {"status": "released"}


# REMOVE async from this function - it should be synchronous
@app.get("/api/system/state")
async def get_system_state_endpoint():
    """API endpoint version"""
    return get_system_state()


def get_system_state():
    """
    Get current system state (synchronous function)
    This is called from both WebSocket and HTTP endpoints
    """
    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "processes": process_manager.get_all_processes(),
        "resources": resource_manager.get_all_resources(),
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlocked_processes": deadlock_info.get("cycle", []),
        "prediction": prediction,
        "graph": detector.get_graph_data()
    }


@app.post("/api/system/reset")
async def reset_system():
    process_manager.reset()
    resource_manager.reset()
    return {"status": "reset"}


async def resolve_deadlock(deadlock_info: Dict):
    # Automated resolution: terminate one process in cycle
    if deadlock_info["cycle"]:
        victim_process = deadlock_info["cycle"][0]
        process_manager.terminate_process(victim_process)

        # Notify all connected clients
        for connection in active_connections:
            try:
                await connection.send_json({
                    "event": "deadlock_resolved",
                    "victim": victim_process
                })
            except:
                pass  # Connection might be closed




@app.post("/api/test/setup-deadlock")
async def setup_deadlock_scenario():
    """
    Set up a classic deadlock scenario for testing
    P1 holds R1, wants R2
    P2 holds R2, wants R1
    """
    # Reset system first
    process_manager.reset()
    resource_manager.reset()

    # Create processes
    p1 = process_manager.create_process("P1", [])
    p2 = process_manager.create_process("P2", [])

    # Create resources
    r1 = resource_manager.create_resource("R1", 1)
    r2 = resource_manager.create_resource("R2", 1)

    # Allocate: P1 holds R1
    resource_manager.allocate_resource(p1, r1)
    process_manager.processes[p1]["allocated"] = [r1]
    process_manager.processes[p1]["requested"] = [r2]  # P1 requests R2

    # Allocate: P2 holds R2
    resource_manager.allocate_resource(p2, r2)
    process_manager.processes[p2]["allocated"] = [r2]
    process_manager.processes[p2]["requested"] = [r1]  # P2 requests R1

    # Detect deadlock
    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "setup_complete",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


@app.post("/api/test/setup-complex-deadlock")
async def setup_complex_deadlock():
    """
    Set up a complex deadlock with 3 processes
    P1 -> R1 (holds), wants R2
    P2 -> R2 (holds), wants R3
    P3 -> R3 (holds), wants R1
    """
    process_manager.reset()
    resource_manager.reset()

    # Create processes
    p1 = process_manager.create_process("P1", [])
    p2 = process_manager.create_process("P2", [])
    p3 = process_manager.create_process("P3", [])

    # Create resources
    r1 = resource_manager.create_resource("R1", 1)
    r2 = resource_manager.create_resource("R2", 1)
    r3 = resource_manager.create_resource("R3", 1)

    # Create circular wait: P1->R1->P2->R2->P3->R3->P1
    resource_manager.allocate_resource(p1, r1)
    process_manager.processes[p1]["allocated"] = [r1]
    process_manager.processes[p1]["requested"] = [r2]

    resource_manager.allocate_resource(p2, r2)
    process_manager.processes[p2]["allocated"] = [r2]
    process_manager.processes[p2]["requested"] = [r3]

    resource_manager.allocate_resource(p3, r3)
    process_manager.processes[p3]["allocated"] = [r3]
    process_manager.processes[p3]["requested"] = [r1]

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "complex_setup_complete",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


@app.post("/api/test/setup-safe-state")
async def setup_safe_state():
    """
    Set up a safe state where no deadlock occurs
    """
    process_manager.reset()
    resource_manager.reset()

    # Create processes
    p1 = process_manager.create_process("P1", [])
    p2 = process_manager.create_process("P2", [])

    # Create resources with multiple instances
    r1 = resource_manager.create_resource("R1", 3)
    r2 = resource_manager.create_resource("R2", 2)

    # Allocate: P1 holds 1 instance of R1
    resource_manager.allocate_resource(p1, r1)
    process_manager.processes[p1]["allocated"] = [r1]

    # P2 holds 1 instance of R2
    resource_manager.allocate_resource(p2, r2)
    process_manager.processes[p2]["allocated"] = [r2]

    # No circular wait - safe state
    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "safe_state_setup",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


# ==================== ADDITIONAL TEST CASES ====================

@app.post("/api/test/dining-philosophers")
async def setup_dining_philosophers():
    """
    Classic Dining Philosophers Problem
    5 philosophers, 5 forks (chopsticks)
    Each philosopher needs 2 forks to eat
    Creates a circular wait deadlock
    """
    process_manager.reset()
    resource_manager.reset()

    # Create 5 philosophers (processes)
    philosophers = []
    for i in range(1, 6):
        p = process_manager.create_process(f"Philosopher_{i}", [])
        philosophers.append(p)

    # Create 5 forks (resources)
    forks = []
    for i in range(1, 6):
        f = resource_manager.create_resource(f"Fork_{i}", 1)
        forks.append(f)

    # Each philosopher holds left fork and requests right fork
    for i in range(5):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % 5]

        # Philosopher holds left fork
        resource_manager.allocate_resource(philosophers[i], left_fork)
        process_manager.processes[philosophers[i]]["allocated"] = [left_fork]

        # Philosopher requests right fork
        process_manager.processes[philosophers[i]]["requested"] = [right_fork]

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "dining_philosophers_deadlock",
        "scenario": "Classic circular wait with 5 philosophers and 5 forks",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction,
        "philosophers": len(philosophers),
        "forks": len(forks)
    }


@app.post("/api/test/reader-writer-deadlock")
async def setup_reader_writer_deadlock():
    """
    Reader-Writer Deadlock Scenario
    Multiple readers and writers competing for shared resources
    """
    process_manager.reset()
    resource_manager.reset()

    # Create readers and writers
    reader1 = process_manager.create_process("Reader_1", [])
    reader2 = process_manager.create_process("Reader_2", [])
    writer1 = process_manager.create_process("Writer_1", [])
    writer2 = process_manager.create_process("Writer_2", [])

    # Create resources: ReadLock, WriteLock, Data
    read_lock = resource_manager.create_resource("ReadLock", 1)
    write_lock = resource_manager.create_resource("WriteLock", 1)
    data = resource_manager.create_resource("SharedData", 1)

    # Writer1 holds WriteLock, wants Data
    resource_manager.allocate_resource(writer1, write_lock)
    process_manager.processes[writer1]["allocated"] = [write_lock]
    process_manager.processes[writer1]["requested"] = [data]

    # Reader1 holds Data, wants ReadLock
    resource_manager.allocate_resource(reader1, data)
    process_manager.processes[reader1]["allocated"] = [data]
    process_manager.processes[reader1]["requested"] = [read_lock]

    # Reader2 holds ReadLock, wants WriteLock
    resource_manager.allocate_resource(reader2, read_lock)
    process_manager.processes[reader2]["allocated"] = [read_lock]
    process_manager.processes[reader2]["requested"] = [write_lock]

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "reader_writer_deadlock",
        "scenario": "Reader-Writer conflict with circular dependencies",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


@app.post("/api/test/banker-unsafe-state")
async def setup_banker_unsafe_state():
    """
    Banker's Algorithm - Unsafe State
    System has resources but allocation leads to unsafe state
    """
    process_manager.reset()
    resource_manager.reset()

    # Create 3 processes
    p0 = process_manager.create_process("P0", [])
    p1 = process_manager.create_process("P1", [])
    p2 = process_manager.create_process("P2", [])

    # Create 3 resource types with multiple instances
    r_a = resource_manager.create_resource("Resource_A", 10)
    r_b = resource_manager.create_resource("Resource_B", 5)
    r_c = resource_manager.create_resource("Resource_C", 7)

    # Allocation: P0 gets 0,1,0 | P1 gets 2,0,0 | P2 gets 3,0,2
    # After allocation, Available = [5,4,5]
    # But this creates unsafe state where no process can complete

    # P0: allocated [0,1,0], needs [7,4,3]
    resource_manager.allocate_resource(p0, r_b)
    process_manager.processes[p0]["allocated"] = [r_b]
    process_manager.processes[p0]["requested"] = [r_a, r_b, r_c]
    process_manager.processes[p0]["wait_time"] = 100

    # P1: allocated [2,0,0], needs [3,2,2]
    resource_manager.allocate_resource(p1, r_a)
    resource_manager.allocate_resource(p1, r_a)
    process_manager.processes[p1]["allocated"] = [r_a, r_a]
    process_manager.processes[p1]["requested"] = [r_a, r_b, r_c]
    process_manager.processes[p1]["wait_time"] = 95

    # P2: allocated [3,0,2], needs [9,0,2]
    resource_manager.allocate_resource(p2, r_a)
    resource_manager.allocate_resource(p2, r_a)
    resource_manager.allocate_resource(p2, r_a)
    resource_manager.allocate_resource(p2, r_c)
    resource_manager.allocate_resource(p2, r_c)
    process_manager.processes[p2]["allocated"] = [r_a, r_a, r_a, r_c, r_c]
    process_manager.processes[p2]["requested"] = [r_a]
    process_manager.processes[p2]["wait_time"] = 110

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "banker_unsafe_state",
        "scenario": "Banker's Algorithm - System in unsafe state",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction,
        "available_resources": {
            "Resource_A": resource_manager.resources[r_a]["available"],
            "Resource_B": resource_manager.resources[r_b]["available"],
            "Resource_C": resource_manager.resources[r_c]["available"]
        }
    }


@app.post("/api/test/hold-and-wait")
async def setup_hold_and_wait():
    """
    Hold and Wait Condition
    Process holds resources while waiting for more
    """
    process_manager.reset()
    resource_manager.reset()

    # Create 4 processes
    p1 = process_manager.create_process("Process_A", [])
    p2 = process_manager.create_process("Process_B", [])
    p3 = process_manager.create_process("Process_C", [])
    p4 = process_manager.create_process("Process_D", [])

    # Create 4 resources
    r1 = resource_manager.create_resource("Printer", 1)
    r2 = resource_manager.create_resource("Scanner", 1)
    r3 = resource_manager.create_resource("HardDisk", 1)
    r4 = resource_manager.create_resource("Memory", 1)

    # Chain: P1->R2, P2->R3, P3->R4, P4->R1 (circular)
    # P1 holds Printer, wants Scanner
    resource_manager.allocate_resource(p1, r1)
    process_manager.processes[p1]["allocated"] = [r1]
    process_manager.processes[p1]["requested"] = [r2]
    process_manager.processes[p1]["wait_time"] = 50

    # P2 holds Scanner, wants HardDisk
    resource_manager.allocate_resource(p2, r2)
    process_manager.processes[p2]["allocated"] = [r2]
    process_manager.processes[p2]["requested"] = [r3]
    process_manager.processes[p2]["wait_time"] = 60

    # P3 holds HardDisk, wants Memory
    resource_manager.allocate_resource(p3, r3)
    process_manager.processes[p3]["allocated"] = [r3]
    process_manager.processes[p3]["requested"] = [r4]
    process_manager.processes[p3]["wait_time"] = 70

    # P4 holds Memory, wants Printer
    resource_manager.allocate_resource(p4, r4)
    process_manager.processes[p4]["allocated"] = [r4]
    process_manager.processes[p4]["requested"] = [r1]
    process_manager.processes[p4]["wait_time"] = 80

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "hold_and_wait_deadlock",
        "scenario": "Hold and Wait - Each process holds one and wants another",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


@app.post("/api/test/no-preemption-deadlock")
async def setup_no_preemption():
    """
    No Preemption Deadlock
    Resources cannot be forcefully taken away
    """
    process_manager.reset()
    resource_manager.reset()

    # Database transaction scenario
    db_trans1 = process_manager.create_process("DB_Transaction_1", [])
    db_trans2 = process_manager.create_process("DB_Transaction_2", [])

    # Critical resources that cannot be preempted
    table_lock = resource_manager.create_resource("TableLock_Users", 1)
    index_lock = resource_manager.create_resource("IndexLock_Orders", 1)

    # Transaction 1 holds table lock, needs index lock
    resource_manager.allocate_resource(db_trans1, table_lock)
    process_manager.processes[db_trans1]["allocated"] = [table_lock]
    process_manager.processes[db_trans1]["requested"] = [index_lock]
    process_manager.processes[db_trans1]["wait_time"] = 150
    process_manager.processes[db_trans1]["state"] = "blocked"

    # Transaction 2 holds index lock, needs table lock
    resource_manager.allocate_resource(db_trans2, index_lock)
    process_manager.processes[db_trans2]["allocated"] = [index_lock]
    process_manager.processes[db_trans2]["requested"] = [table_lock]
    process_manager.processes[db_trans2]["wait_time"] = 140
    process_manager.processes[db_trans2]["state"] = "blocked"

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "no_preemption_deadlock",
        "scenario": "Database transactions - No preemption allowed",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction
    }


@app.post("/api/test/large-scale-deadlock")
async def setup_large_scale():
    """
    Large Scale Deadlock
    10 processes and 8 resources with complex dependencies
    Tests system scalability
    """
    process_manager.reset()
    resource_manager.reset()

    # Create 10 processes
    processes = []
    for i in range(1, 11):
        p = process_manager.create_process(f"Worker_{i}", [])
        processes.append(p)

    # Create 8 resources
    resources = []
    for i in range(1, 9):
        r = resource_manager.create_resource(f"Resource_{i}", 1)
        resources.append(r)

    # Create complex circular dependencies
    for i in range(10):
        current_resource = resources[i % 8]
        next_resource = resources[(i + 1) % 8]

        # Process holds current, wants next
        resource_manager.allocate_resource(processes[i], current_resource)
        process_manager.processes[processes[i]]["allocated"] = [current_resource]
        process_manager.processes[processes[i]]["requested"] = [next_resource]
        process_manager.processes[processes[i]]["wait_time"] = 50 + (i * 10)

    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "large_scale_deadlock",
        "scenario": "Large scale - 10 processes, 8 resources, complex circular wait",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction,
        "process_count": len(processes),
        "resource_count": len(resources)
    }


@app.post("/api/test/near-deadlock-high-risk")
async def setup_near_deadlock():
    """
    Near Deadlock State - High Risk
    System is very close to deadlock but not quite there yet
    Tests AI prediction capability
    """
    process_manager.reset()
    resource_manager.reset()

    # Create 3 processes
    p1 = process_manager.create_process("CriticalProcess_1", [])
    p2 = process_manager.create_process("CriticalProcess_2", [])
    p3 = process_manager.create_process("CriticalProcess_3", [])

    # Create 3 resources with very limited availability
    r1 = resource_manager.create_resource("CriticalResource_1", 1)
    r2 = resource_manager.create_resource("CriticalResource_2", 1)
    r3 = resource_manager.create_resource("CriticalResource_3", 1)

    # High resource contention, long wait times
    # P1 holds R1, might request R2 soon
    resource_manager.allocate_resource(p1, r1)
    process_manager.processes[p1]["allocated"] = [r1]
    process_manager.processes[p1]["wait_time"] = 120
    process_manager.processes[p1]["state"] = "waiting"

    # P2 holds R2, might request R3 soon
    resource_manager.allocate_resource(p2, r2)
    process_manager.processes[p2]["allocated"] = [r2]
    process_manager.processes[p2]["wait_time"] = 115
    process_manager.processes[p2]["state"] = "waiting"

    # P3 holds R3, might request R1 soon (would complete circle)
    resource_manager.allocate_resource(p3, r3)
    process_manager.processes[p3]["allocated"] = [r3]
    process_manager.processes[p3]["wait_time"] = 110
    process_manager.processes[p3]["state"] = "waiting"

    # High resource utilization (100%)
    deadlock_info = detector.detect_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    prediction = predictor.predict_deadlock(
        process_manager.processes,
        resource_manager.resources
    )

    return {
        "status": "near_deadlock_high_risk",
        "scenario": "High risk - 100% resource utilization, long wait times",
        "deadlock_detected": deadlock_info["has_deadlock"],
        "deadlock_info": deadlock_info,
        "ai_prediction": prediction,
        "warning": "System is one request away from deadlock!"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)