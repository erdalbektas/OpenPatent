import multiprocessing
import time
import queue
from typing import Dict, Any, Callable
from patent_suite.agents.base import BaseAgent

class AgentSandbox:
    """
    Wraps agent execution in a separate process with a timeout for safety.
    Ensures custom agents don't crash or hang the main system.
    """
    
    @staticmethod
    def _run_agent_process(agent: BaseAgent, task: str, context: Dict[str, Any], result_queue: multiprocessing.Queue):
        try:
            output = agent.run(task, context)
            result_queue.put({"status": "success", "output": output})
        except Exception as e:
            result_queue.put({"status": "error", "message": str(e)})

    @classmethod
    def run_safe(cls, agent: BaseAgent, task: str, context: Dict[str, Any], timeout_seconds: int = 60) -> Dict[str, Any]:
        """
        Executes an agent's run method with a strict timeout.
        """
        result_queue = multiprocessing.Queue()
        
        process = multiprocessing.Process(
            target=cls._run_agent_process,
            args=(agent, task, context, result_queue)
        )
        
        print(f"Sandbox: Starting execution for {agent.name} (Timeout: {timeout_seconds}s)...")
        process.start()
        
        try:
            # Wait for result with timeout
            result = result_queue.get(timeout=timeout_seconds)
            process.join()
            return result
        except queue.Empty:
            print(f"Sandbox: TIMEOUT reached for {agent.name}. Terminating process.")
            process.terminate()
            process.join()
            return {
                "status": "error",
                "message": f"Custom Agent {agent.name} Failed: Execution timed out after {timeout_seconds} seconds."
            }
        except Exception as e:
            print(f"Sandbox: Unexpected error during execution: {e}")
            if process.is_alive():
                process.terminate()
            process.join()
            return {
                "status": "error",
                "message": f"Custom Agent {agent.name} Failed: {str(e)}"
            }

if __name__ == "__main__":
    # Test with a hanging agent
    class HangingAgent(BaseAgent):
        @property
        def name(self): return "Hanger"
        @property
        def description(self): return "Hangs for 5 seconds."
        def run(self, task, context):
            time.sleep(5)
            return "Done"
        def get_tools(self): return []

    agent = HangingAgent()
    
    # Test successful within timeout
    print("--- Test 1: Successful Execution ---")
    result = AgentSandbox.run_safe(agent, "test", {}, timeout_seconds=10)
    print(f"Result: {result}")

    # Test timeout
    print("\n--- Test 2: Timeout ---")
    result = AgentSandbox.run_safe(agent, "test", {}, timeout_seconds=2)
    print(f"Result: {result}")
