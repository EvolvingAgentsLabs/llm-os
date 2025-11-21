#!/usr/bin/env python3
"""
Demo script for Qiskit Studio Backend - LLM OS Edition

This script demonstrates the key features:
1. Code generation via chat endpoint
2. Direct code execution
3. Learner → Follower cost savings
4. Statistics monitoring
"""

import asyncio
import httpx
import json
from pathlib import Path


class QiskitStudioDemo:
    """Demo client for Qiskit Studio Backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat(self, message: str, session_id: str = "demo"):
        """Send a chat message"""
        response = await self.client.post(
            f"{self.base_url}/chat",
            json={
                "messages": [{"role": "user", "content": message}],
                "session_id": session_id
            }
        )
        return response.json()

    async def run_code(self, code: str):
        """Execute Qiskit code"""
        response = await self.client.post(
            f"{self.base_url}/run",
            json={"input_value": code}
        )
        return response.json()

    async def get_stats(self):
        """Get backend statistics"""
        response = await self.client.get(f"{self.base_url}/stats")
        return response.json()

    async def close(self):
        """Close the client"""
        await self.client.aclose()


async def demo_chat_code_generation():
    """Demo 1: Generate quantum code via chat"""
    print("\n" + "="*60)
    print("DEMO 1: Code Generation via Chat Endpoint")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        print("\n📝 Request: Generate a Bell state circuit")
        result = await demo.chat("Create a Bell state circuit and measure it")

        print(f"\n🤖 Agent: {result['metadata']['agent']}")
        print(f"🎯 Mode: {result['metadata']['mode']}")
        print(f"💰 Cost: ${result['metadata']['cost']:.4f}")
        print(f"💾 Cached: {result['metadata']['cached']}")
        print(f"\n📄 Response:\n{result['content'][:500]}...")

    finally:
        await demo.close()


async def demo_code_execution():
    """Demo 2: Direct code execution"""
    print("\n" + "="*60)
    print("DEMO 2: Direct Code Execution")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        code = """
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.primitives import Sampler

# Create a 2-qubit Bell state
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print("Circuit created:")
print(qc)

# Simulate
sampler = Sampler()
job = sampler.run(qc, shots=100)
result = job.result()

print("\\nQuasi-probabilities:")
print(result.quasi_dists[0])
"""

        print("\n⚙️  Executing Qiskit code...")
        result = await demo.run_code(code)

        print(f"\n✅ Execution Output:\n{result['output']}")

    finally:
        await demo.close()


async def demo_cost_savings():
    """Demo 3: Learner → Follower cost savings"""
    print("\n" + "="*60)
    print("DEMO 3: Learner → Follower Cost Savings")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        message = "Create a 3-qubit GHZ state circuit"

        # First request (LEARNER mode)
        print(f"\n📝 First request: {message}")
        print("   Mode: LEARNER (will reason and generate)")
        result1 = await demo.chat(message, session_id="cost-demo-1")

        cost1 = result1['metadata']['cost']
        mode1 = result1['metadata']['mode']
        cached1 = result1['metadata']['cached']

        print(f"   💰 Cost: ${cost1:.4f}")
        print(f"   🎯 Mode: {mode1}")
        print(f"   💾 Cached: {cached1}")

        # Second request (FOLLOWER mode - should be cached)
        print(f"\n📝 Second request: {message}")
        print("   Mode: FOLLOWER (should use cache)")
        result2 = await demo.chat(message, session_id="cost-demo-2")

        cost2 = result2['metadata']['cost']
        mode2 = result2['metadata']['mode']
        cached2 = result2['metadata']['cached']

        print(f"   💰 Cost: ${cost2:.4f}")
        print(f"   🎯 Mode: {mode2}")
        print(f"   💾 Cached: {cached2}")

        # Summary
        print("\n📊 Summary:")
        print(f"   First request:  ${cost1:.4f} ({mode1})")
        print(f"   Second request: ${cost2:.4f} ({mode2})")

        if cost2 == 0.0:
            print(f"   ✨ Savings: 100% (FOLLOWER mode activated!)")
        else:
            savings = ((cost1 - cost2) / cost1 * 100) if cost1 > 0 else 0
            print(f"   💡 Savings: {savings:.1f}%")

    finally:
        await demo.close()


async def demo_security():
    """Demo 4: Security hooks in action"""
    print("\n" + "="*60)
    print("DEMO 4: Security Hooks")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        # Try to execute malicious code
        malicious_code = """
import os
os.system("echo 'Attempting system access...'")
"""

        print("\n⚠️  Attempting to execute malicious code:")
        print(malicious_code)
        print("\n🔒 LLM OS Security Hooks should block this...")

        result = await demo.run_code(malicious_code)

        print(f"\n✅ Security Response:\n{result['output']}")

        if "Security Error" in result['output']:
            print("\n✅ SUCCESS: Malicious code was blocked!")
        else:
            print("\n⚠️  WARNING: Code was not blocked (check security hooks)")

    finally:
        await demo.close()


async def demo_statistics():
    """Demo 5: View backend statistics"""
    print("\n" + "="*60)
    print("DEMO 5: Backend Statistics")
    print("="*60)

    demo = QiskitStudioDemo()

    try:
        print("\n📊 Fetching statistics...")
        stats = await demo.get_stats()

        print("\n💰 Token Economy:")
        print(f"   Budget:    ${stats['token_economy']['budget_usd']:.2f}")
        print(f"   Spent:     ${stats['token_economy']['spent_usd']:.2f}")
        print(f"   Remaining: ${stats['token_economy']['remaining_usd']:.2f}")
        print(f"   Transactions: {stats['token_economy']['transactions']}")

        print("\n🧠 Memory:")
        print(f"   Total Traces:        {stats['memory']['total_traces']}")
        print(f"   High-Confidence:     {stats['memory']['high_confidence_traces']}")
        print(f"   Facts:               {stats['memory']['facts']}")

        print("\n🤖 Agents:")
        print(f"   Registered: {stats['agents']['registered']}")
        print(f"   Available:  {', '.join(stats['agents']['available'])}")

        print("\n💬 Sessions:")
        print(f"   Active:         {stats['sessions']['active']}")
        print(f"   Total Messages: {stats['sessions']['total_messages']}")

    finally:
        await demo.close()


async def run_all_demos():
    """Run all demos"""
    print("\n" + "="*70)
    print(" "*15 + "Qiskit Studio Backend - LLM OS Edition")
    print(" "*25 + "Demo Suite")
    print("="*70)

    try:
        # Check if server is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/")
                if response.status_code != 200:
                    print("\n❌ Error: Backend server is not responding")
                    print("   Start the server with: ./run.sh")
                    return
            except httpx.ConnectError:
                print("\n❌ Error: Cannot connect to backend server")
                print("   Start the server with: ./run.sh")
                return

        # Run demos
        await demo_chat_code_generation()
        await asyncio.sleep(1)

        await demo_code_execution()
        await asyncio.sleep(1)

        await demo_cost_savings()
        await asyncio.sleep(1)

        await demo_security()
        await asyncio.sleep(1)

        await demo_statistics()

        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Check the backend logs for detailed execution info")
        print("  2. Try the Qiskit Studio frontend at http://localhost:3000")
        print("  3. Review the README.md for more examples")
        print()

    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_demos())
