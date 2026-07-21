from typing import Dict, Any
from services.llm_service import LLMService


class CriticAgent:
    """
    Evaluates candidate generated response for factual grounding, accuracy, and completeness.
    """

    def __init__(self, llm_service: LLMService = None):
        self.llm = llm_service or LLMService()

    def evaluate(self, question: str, response: str, context: str) -> Dict[str, Any]:
        system_instruction = (
            "You are a rigorous Scientific Critic. Evaluate if the proposed response accurately and fully "
            "answers the user's question using the provided research context."
        )

        prompt = (
            f"CRITIC EVALUATION\n"
            f"User Question: {question}\n\n"
            f"Provided Context: {context[:2000]}\n\n"
            f"Candidate Response: {response}\n\n"
            "Task: Is the answer good, accurate, and grounded? Output DECISION: GOOD or DECISION: RETRY followed by FEEDBACK."
        )

        eval_output = self.llm.generate(prompt, system_instruction=system_instruction)

        is_good = "DECISION: GOOD" in eval_output.upper() or "GOOD" in eval_output.upper()

        return {
            "is_good": is_good,
            "feedback": eval_output,
            "eval_raw": eval_output
        }
