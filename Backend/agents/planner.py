from typing import Dict, Any, List
from services.llm_service import LLMService


class PlannerAgent:
    """
    Decomposes user question into targeted sub-tasks and sub-queries for downstream agents.
    """

    def __init__(self, llm_service: LLMService = None):
        self.llm = llm_service or LLMService()

    def plan(self, question: str, feedback: str = None) -> Dict[str, Any]:
        system_instruction = (
            "You are a Senior AI Research Planner. Break down the user query into specific sub-tasks."
        )
        prompt = f"User Question: {question}\n"
        if feedback:
            prompt += f"Previous Critic Feedback (for retry): {feedback}\n"

        prompt += (
            "Formulate 3 sub-queries for document vector research and web search.\n"
            "Output bullet points."
        )

        response = self.llm.generate(prompt, system_instruction=system_instruction)

        sub_queries = [
            line.strip("- *").strip()
            for line in response.split("\n")
            if line.strip().startswith(("-", "*", "1.", "2.", "3."))
        ]
        if not sub_queries:
            sub_queries = [question]

        return {
            "plan_summary": response,
            "sub_queries": sub_queries,
            "status": "planned"
        }
