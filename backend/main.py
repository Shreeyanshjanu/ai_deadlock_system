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



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)