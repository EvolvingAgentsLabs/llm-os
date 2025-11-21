"""
RoboOS - FastAPI Server

Production-ready REST API server for robot control via LLM OS.

This server provides:
- Natural language robot control endpoints
- Safety monitoring and reporting
- State visualization (cockpit/operator views)
- WebSocket for real-time updates
- Session management
"""

import sys
import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from boot.llm_os import LLMOS
from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
from agents.operator import OPERATOR_AGENT_CONFIG
from agents.safety_officer import SAFETY_OFFICER_CONFIG
from robot_state import get_robot_state, reset_robot_state
from safety_hook import get_safety_hook


# ============================================================================
# Pydantic Models
# ============================================================================

class CommandRequest(BaseModel):
    """Request model for robot commands."""
    command: str
    session_id: Optional[str] = "default"
    agent: Optional[str] = "operator"  # or "safety_officer"


class MoveRequest(BaseModel):
    """Direct movement request."""
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    theta: Optional[float] = None


class ToolRequest(BaseModel):
    """Tool activation request."""
    activate: bool


class ViewRequest(BaseModel):
    """Camera view request."""
    view_type: str = "cockpit"  # or "operator"


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="RoboOS API",
    description="LLM OS-powered robot control system",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State
# ============================================================================

llmos_instance: Optional[LLMOS] = None
operator_agent = None
safety_officer_agent = None
websocket_connections: list[WebSocket] = []


# ============================================================================
# Initialization
# ============================================================================

def initialize_llmos():
    """Initialize LLM OS instance and agents."""
    global llmos_instance, operator_agent, safety_officer_agent

    if llmos_instance is not None:
        return  # Already initialized

    # Create LLM OS instance
    llmos_instance = LLMOS()

    # Register all robot controller tools
    for tool in ROBOT_CONTROLLER_TOOLS:
        llmos_instance.register_tool(
            name=tool['name'],
            func=tool['function'],
            description=tool['description']
        )

    # Register safety hook
    llmos_instance.register_hook('pre_tool_use', get_safety_hook())

    # Create operator agent
    operator_agent = llmos_instance.create_agent(
        name=OPERATOR_AGENT_CONFIG['name'],
        mode=OPERATOR_AGENT_CONFIG['mode'],
        system_prompt=OPERATOR_AGENT_CONFIG['system_prompt']
    )

    # Create safety officer agent (only monitoring tools)
    safety_tools = ['get_status', 'get_camera_feed', 'emergency_stop']
    safety_officer_agent = llmos_instance.create_agent(
        name=SAFETY_OFFICER_CONFIG['name'],
        mode=SAFETY_OFFICER_CONFIG['mode'],
        system_prompt=SAFETY_OFFICER_CONFIG['system_prompt'],
        available_tools=safety_tools
    )

    print("✓ LLM OS initialized")
    print("✓ Operator agent ready")
    print("✓ Safety officer agent ready")
    print("✓ Safety hook registered")


@app.on_event("startup")
async def startup_event():
    """Initialize on server startup."""
    print("\n" + "="*70)
    print("  RoboOS Server Starting...")
    print("="*70 + "\n")
    initialize_llmos()
    print("\n✓ Server ready!")
    print(f"  API docs: http://localhost:8000/docs")
    print(f"  Health: http://localhost:8000/health\n")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "RoboOS API",
        "version": "1.0.0",
        "status": "operational",
        "message": "LLM OS-powered robot control system",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "state": "/state",
            "command": "/command [POST]",
            "move": "/move [POST]",
            "tool": "/tool [POST]",
            "view": "/view [POST]",
            "safety": "/safety",
            "reset": "/reset [POST]",
            "emergency": "/emergency [POST]"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    robot_state = get_robot_state()
    return {
        "status": "healthy" if not robot_state.emergency_stop else "emergency_stop",
        "timestamp": datetime.now().isoformat(),
        "emergency_stop": robot_state.emergency_stop,
        "llmos_ready": llmos_instance is not None
    }


@app.get("/state")
async def get_state():
    """Get current robot state."""
    robot_state = get_robot_state()
    return {
        "state": robot_state.get_state(),
        "safety_limits": robot_state.safety_limits.to_dict(),
        "recent_actions": robot_state.history[-10:]
    }


@app.post("/command")
async def execute_command(request: CommandRequest):
    """
    Execute a natural language command via the operator or safety officer agent.

    Example requests:
    - {"command": "Move 30cm to the right"}
    - {"command": "Show me the cockpit view"}
    - {"command": "Check safety status", "agent": "safety_officer"}
    """
    if llmos_instance is None:
        initialize_llmos()

    # Select agent
    agent = operator_agent if request.agent == "operator" else safety_officer_agent

    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        # Execute command
        response = await agent.run(request.command)

        return {
            "success": True,
            "command": request.command,
            "agent": request.agent,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/move")
async def direct_move(request: MoveRequest):
    """
    Direct movement endpoint (bypasses natural language, uses tool directly).

    WARNING: This still goes through the safety hook!
    """
    if llmos_instance is None:
        initialize_llmos()

    try:
        robot_state = get_robot_state()
        current = robot_state.position

        # Use provided values or keep current
        x = request.x if request.x is not None else current.x
        y = request.y if request.y is not None else current.y
        z = request.z if request.z is not None else current.z
        theta = request.theta if request.theta is not None else current.theta

        # Import tool function
        from plugins.robot_controller import move_to

        # Execute move (safety hook will validate)
        result = await move_to(x, y, z, theta)

        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool")
async def control_tool(request: ToolRequest):
    """Activate or deactivate the robot tool."""
    if llmos_instance is None:
        initialize_llmos()

    try:
        from plugins.robot_controller import toggle_tool
        result = await toggle_tool(request.activate)

        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/view")
async def get_view(request: ViewRequest):
    """Get camera feed view (cockpit or operator)."""
    try:
        from plugins.robot_controller import get_camera_feed
        view = await get_camera_feed(request.view_type)

        return {
            "success": True,
            "view_type": request.view_type,
            "view": view,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/safety")
async def get_safety_status():
    """Get safety status and violation history."""
    robot_state = get_robot_state()
    safety_hook = get_safety_hook()

    is_safe, reason = robot_state.safety_limits.is_position_safe(robot_state.position)

    return {
        "current_position_safe": is_safe,
        "reason": reason,
        "emergency_stop": robot_state.emergency_stop,
        "violations": safety_hook.get_violations_summary(),
        "safety_limits": robot_state.safety_limits.to_dict()
    }


@app.post("/reset")
async def reset_system():
    """Reset robot to home position and clear state."""
    reset_robot_state()
    safety_hook = get_safety_hook()
    safety_hook.reset_violations()

    return {
        "success": True,
        "message": "Robot reset to home position",
        "state": get_robot_state().get_state()
    }


@app.post("/emergency")
async def trigger_emergency():
    """Trigger emergency stop."""
    from plugins.robot_controller import emergency_stop
    result = await emergency_stop()

    # Notify WebSocket clients
    await broadcast_to_websockets({
        "type": "emergency_stop",
        "message": "EMERGENCY STOP ACTIVATED",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "result": result
    }


# ============================================================================
# WebSocket for Real-Time Updates
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time robot state updates.

    Clients can connect to receive live updates when robot state changes.
    """
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Send periodic state updates
            robot_state = get_robot_state()
            await websocket.send_json({
                "type": "state_update",
                "state": robot_state.get_state(),
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast a message to all connected WebSocket clients."""
    for connection in websocket_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_json(message)
        except Exception:
            # Remove dead connections
            websocket_connections.remove(connection)


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
