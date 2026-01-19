import json

class InterrogatorAgent:
    def __init__(self):
        self.persona = "Expert Technical Interrogator"
        self.instruction = (
            "Identify technical terms that lack implementation details. "
            "Formulate 3 specific 'How' questions."
        )

    def run(self, disclosure_text):
        """
        Analyzes the disclosure and generates 3 probing questions.
        """
        print(f"InterrogatorAgent: Analyzing disclosure for technical gaps...")
        
        # Mock logic to 'extract' terms lacking detail based on the toaster example
        # In a real scenario, this would be an LLM call.
        
        # Simulated extraction
        gaps = ["laser rasterization", "optical browning sensor", "micro-controller feedback"]
        
        questions = [
            {
                "term": "laser rasterization",
                "question": "How is the laser beam rasterized to ensure uniform toasting without creating 'hot spots' on the bread?"
            },
            {
                "term": "optical browning sensor",
                "question": "How does the optical sensor distinguish between a desired dark brown pattern and a burnt surface?"
            },
            {
                "term": "micro-controller feedback",
                "question": "How does the micro-controller adjust the laser intensity in real-time based on the sensor's input?"
            }
        ]
        
        output = {
            "agent": self.persona,
            "instruction": self.instruction,
            "questions": questions
        }
        
        return output

if __name__ == "__main__":
    agent = InterrogatorAgent()
    result = agent.run("A toaster that uses lasers instead of heating coils.")
    print(json.dumps(result, indent=4))
