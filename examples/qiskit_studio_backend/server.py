#!/usr/bin/env python3
"""
Qiskit Studio Backend - LLM OS Edition

This FastAPI server acts as a bridge between the Qiskit Studio frontend
and the LLM OS backend, replacing the original Maestro-based microservices
(chat-agent, codegen-agent, coderun-agent) with a unified LLM OS implementation.

Key features:
- Drop-in replacement for qiskit-studio API endpoints
- Learner/Follower mode for cost-efficient repeated tasks
- Orchestrator mode for complex reasoning
- Built-in security hooks
- Unified memory management
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
import sys
import logging
import json
from typing import Optional, Dict, Any, List

# Add llmos to path
LLMOS_ROOT = Path(__file__).parents[2] / "llmos"
sys.path.insert(0, str(LLMOS_ROOT))

from boot import LLMOS
from kernel.component_registry import ComponentRegistry

# Import our custom agents and tools
sys.path.insert(0, str(Path(__file__).parent))
from agents import QUANTUM_ARCHITECT, QUANTUM_TUTOR
from plugins.qiskit_tools import execute_qiskit_code, validate_qiskit_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Qiskit Studio Backend - LLM OS Edition",
    description="Drop-in replacement for qiskit-studio backend using LLM OS",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM OS instance (initialized on startup)
os_instance: Optional[LLMOS] = None
session_memory: Dict[str, List[Dict[str, str]]] = {}  # Session-based chat history


def analyze_intent(user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Analyze user intent to determine routing strategy.

    Returns:
        Dict with:
        - agent: "quantum-architect" or "quantum-tutor"
        - mode: "LEARNER", "FOLLOWER", or "AUTO"
        - is_coding_task: bool
    """
    user_input_lower = user_input.lower()

    # Coding indicators
    coding_keywords = [
        "code", "circuit", "implement", "create", "generate", "write",
        "build", "program", "qubits", "gates", "measure", "execute",
        "bell state", "ghz", "grover", "shor", "vqe", "qaoa"
    ]

    # Question indicators
    question_keywords = [
        "what", "how", "why", "when", "where", "explain", "describe",
        "tell me", "difference", "compare", "teach", "help me understand"
    ]

    # Check for coding task
    is_coding = any(keyword in user_input_lower for keyword in coding_keywords)
    is_question = any(keyword in user_input_lower for keyword in question_keywords)

    # Determine agent
    if is_coding and not is_question:
        agent = "quantum-architect"
        # Check if it's a repeated pattern (FOLLOWER candidate)
        # In a real implementation, this would check memory for similar tasks
        mode = "AUTO"  # Let LLM OS dispatcher decide
    elif is_question and not is_coding:
        agent = "quantum-tutor"
        mode = "ORCHESTRATOR"  # Tutor uses orchestration for knowledge retrieval
    elif is_coding and is_question:
        # "How do I create a Bell state?" - hybrid
        agent = "quantum-architect"  # Architect can explain + provide code
        mode = "AUTO"
    else:
        # Default to tutor for general queries
        agent = "quantum-tutor"
        mode = "ORCHESTRATOR"

    logger.info(f"Intent analysis: agent={agent}, mode={mode}, is_coding={is_coding}")

    return {
        "agent": agent,
        "mode": mode,
        "is_coding_task": is_coding
    }


@app.on_event("startup")
async def startup():
    """Initialize LLM OS on server startup"""
    global os_instance

    logger.info("="*60)
    logger.info("Starting Qiskit Studio Backend (LLM OS Edition)")
    logger.info("="*60)

    # Initialize LLM OS with a reasonable budget
    os_instance = LLMOS(
        budget_usd=50.0,  # $50 budget for quantum computing tasks
        project_name="qiskit_studio_session"
    )

    # Register our custom Qiskit tools
    logger.info("Registering Qiskit tools...")
    os_instance.component_registry.register_tool(execute_qiskit_code)
    os_instance.component_registry.register_tool(validate_qiskit_code)

    # Register our custom agents
    logger.info("Registering specialized quantum agents...")
    os_instance.component_registry.register_agent(QUANTUM_ARCHITECT)
    os_instance.component_registry.register_agent(QUANTUM_TUTOR)

    # Boot the OS
    await os_instance.boot()

    # Pre-load any quantum computing knowledge into L4 memory
    # This would normally load Qiskit documentation, but we'll skip for now
    logger.info("Backend initialization complete!")
    logger.info("="*60)
    print()


@app.on_event("shutdown")
async def shutdown():
    """Shutdown LLM OS gracefully"""
    global os_instance

    if os_instance:
        logger.info("Shutting down LLM OS...")
        await os_instance.shutdown()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Qiskit Studio Backend - LLM OS Edition",
        "version": "1.0.0",
        "llm_os_running": os_instance is not None and os_instance._running
    }


@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Chat endpoint - handles both conversational and code generation requests.

    This is the drop-in replacement for:
    - Original chat-agent (RAG-based Q&A)
    - Original codegen-agent (code generation)

    The LLM OS dispatcher automatically routes to the appropriate agent
    and mode (Learner/Follower/Orchestrator).

    Request format:
    {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ],
        "session_id": "optional-session-id"
    }

    Response format:
    {
        "role": "assistant",
        "content": "...",
        "metadata": {
            "agent": "quantum-architect",
            "mode": "FOLLOWER",
            "cost": 0.0,
            "cached": true
        }
    }
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    try:
        data = await request.json()
        messages = data.get("messages", [])
        session_id = data.get("session_id", "default")

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the latest user message
        user_message = messages[-1].get("content", "")

        if not user_message:
            raise HTTPException(status_code=400, detail="Empty user message")

        # Get or create session history
        if session_id not in session_memory:
            session_memory[session_id] = []

        conversation_history = session_memory[session_id]

        # Analyze intent
        intent = analyze_intent(user_message, conversation_history)

        logger.info(f"Processing chat request: {user_message[:100]}...")
        logger.info(f"Routing to agent: {intent['agent']}, mode: {intent['mode']}")

        # Build enhanced prompt with conversation context
        if conversation_history:
            context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            enhanced_prompt = f"""Previous conversation:
{context}

Current request: {user_message}"""
        else:
            enhanced_prompt = user_message

        # Execute through LLM OS
        # The dispatcher will automatically:
        # 1. Check if this is a repeated pattern (FOLLOWER mode - FREE)
        # 2. Route to appropriate agent
        # 3. Use memory for context
        # 4. Apply security hooks

        result = await os_instance.execute(
            goal=enhanced_prompt,
            mode=intent["mode"],
            max_cost_usd=2.0  # Max $2 per request
        )

        # Extract response
        response_text = result.get("output", "")
        cost = result.get("cost", 0.0)
        mode_used = result.get("mode", intent["mode"])
        cached = cost == 0.0  # If cost is 0, it was cached (FOLLOWER mode)

        # Update session memory
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response_text})
        session_memory[session_id] = conversation_history

        # Log interesting stats
        if cached:
            logger.info("✨ FOLLOWER mode activated - Request served from cache (FREE!)")
        else:
            logger.info(f"💰 Request cost: ${cost:.4f}")

        # Return response in format expected by frontend
        return {
            "role": "assistant",
            "content": response_text,
            "metadata": {
                "agent": intent["agent"],
                "mode": mode_used,
                "cost": cost,
                "cached": cached,
                "session_id": session_id
            }
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_endpoint(request: Request):
    """
    Direct code execution endpoint.

    This is the drop-in replacement for the original coderun-agent.

    Instead of a separate microservice, we use the LLM OS Somatic Layer
    (execute_qiskit_code tool) with built-in security hooks.

    Request format:
    {
        "input_value": "python code here",
        "ibm_token": "optional-ibm-quantum-token",
        "channel": "ibm_quantum",
        "instance": "optional-crn",
        "region": "optional-region"
    }

    Response format:
    {
        "output": "execution output here"
    }
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    try:
        data = await request.json()
        code = data.get("input_value", "")

        if not code:
            raise HTTPException(status_code=400, detail="No code provided")

        # Extract IBM Quantum config (optional)
        ibm_token = data.get("ibm_token")
        channel = data.get("channel", "ibm_quantum")
        instance = data.get("instance")
        region = data.get("region")

        logger.info(f"Executing Qiskit code ({len(code)} chars)...")

        # Execute using the Somatic Layer tool
        # This goes through LLM OS security hooks automatically
        use_simulator = not bool(ibm_token)  # Use simulator if no token

        output = await execute_qiskit_code(
            code=code,
            use_simulator=use_simulator,
            ibm_token=ibm_token,
            channel=channel,
            instance=instance,
            region=region
        )

        logger.info("Code execution completed successfully")

        return JSONResponse({"output": output})

    except Exception as e:
        logger.error(f"Error in run endpoint: {str(e)}", exc_info=True)
        error_output = f"Error executing code: {str(e)}"
        return JSONResponse({"output": error_output})


@app.get("/stats")
async def stats_endpoint():
    """
    Statistics endpoint - shows LLM OS performance metrics.

    This is a bonus endpoint that showcases LLM OS capabilities.
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    # Get memory statistics
    mem_stats = os_instance.memory_query.get_memory_statistics()

    # Get token economy stats
    total_spent = sum(log["cost"] for log in os_instance.token_economy.spend_log)
    balance = os_instance.token_economy.balance

    return {
        "token_economy": {
            "budget_usd": 50.0,
            "spent_usd": total_spent,
            "remaining_usd": balance,
            "transactions": len(os_instance.token_economy.spend_log)
        },
        "memory": {
            "total_traces": mem_stats.get("total_traces", 0),
            "high_confidence_traces": mem_stats.get("high_confidence_count", 0),
            "facts": mem_stats.get("facts_count", 0)
        },
        "agents": {
            "registered": len(os_instance.component_registry.list_agents()),
            "available": [
                agent["name"]
                for agent in os_instance.component_registry.list_agents()
            ]
        },
        "sessions": {
            "active": len(session_memory),
            "total_messages": sum(len(history) for history in session_memory.values())
        }
    }


@app.post("/clear_session")
async def clear_session_endpoint(request: Request):
    """
    Clear a chat session's history.

    Request format:
    {
        "session_id": "session-id-to-clear"
    }
    """
    data = await request.json()
    session_id = data.get("session_id", "default")

    if session_id in session_memory:
        del session_memory[session_id]
        logger.info(f"Cleared session: {session_id}")

    return {"status": "ok", "session_id": session_id}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Qiskit Studio Backend powered by LLM OS"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    logger.info(f"Starting server on {args.host}:{args.port}")

    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
