import logging
from typing import Dict, Any, List, TypedDict, Optional
from sqlalchemy.orm import Session

from agents.planner import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.web_agent import WebAgent
from agents.memory_agent import MemoryAgent
from agents.citation_agent import CitationAgent
from agents.critic_agent import CriticAgent
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    question: str
    user_id: Optional[str]
    document_id: Optional[str]
    db: Optional[Session]
    plan_summary: Optional[str]
    sub_queries: List[str]
    doc_chunks: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    memory_context: List[Dict[str, Any]]
    citations: List[str]
    sources: List[Dict[str, Any]]
    compiled_context: str
    candidate_answer: str
    critic_is_good: bool
    critic_feedback: Optional[str]
    retry_count: int
    final_answer: str


class ResearchAgentWorkflow:
    """
    Executes the multi-agent graph corresponding to Image 3 architecture:
    Planner -> [Research, Web, Memory, Citation] -> Context Builder -> LLM Generator -> Critic -> Retry Loop / Final Answer.
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.web_agent = WebAgent()
        self.memory_agent = MemoryAgent()
        self.citation_agent = CitationAgent()
        self.critic_agent = CriticAgent()
        self.llm = LLMService()

    def run(
        self,
        question: str,
        user_id: str = None,
        document_id: str = None,
        db: Session = None,
        mode: str = "research",
        max_retries: int = 1
    ) -> Dict[str, Any]:
        state: AgentState = {
            "question": question,
            "user_id": user_id,
            "document_id": document_id,
            "db": db,
            "plan_summary": "",
            "sub_queries": [],
            "doc_chunks": [],
            "web_results": [],
            "memory_context": [],
            "citations": [],
            "sources": [],
            "compiled_context": "",
            "candidate_answer": "",
            "critic_is_good": False,
            "critic_feedback": None,
            "retry_count": 0,
            "final_answer": ""
        }

        max_citations = 4 if mode == "slides" else 9

        while state["retry_count"] <= max_retries:
            # 1. Planner Node
            plan_res = self.planner.plan(state["question"], feedback=state["critic_feedback"])
            state["plan_summary"] = plan_res["plan_summary"]
            state["sub_queries"] = plan_res["sub_queries"]

            # 2. Worker Agents Parallel Execution
            state["doc_chunks"] = self.research_agent.search(
                sub_queries=state["sub_queries"],
                document_id=state["document_id"]
            )
            state["web_results"] = self.web_agent.search(sub_queries=state["sub_queries"])
            state["memory_context"] = self.memory_agent.get_context(
                user_id=state["user_id"],
                db=state["db"],
                query=state["question"],
                document_id=state["document_id"],
                mode=mode
            )

            # 3. Citation Agent Node
            cit_res = self.citation_agent.process(
                doc_chunks=state["doc_chunks"],
                web_results=state["web_results"],
                max_citations=max_citations
            )
            state["citations"] = cit_res["citations"]
            state["sources"] = cit_res["sources"]

            # 4. Context Builder Node
            context_parts = []
            if state["doc_chunks"]:
                context_parts.append("--- DOCUMENT CONTEXT ---")
                for c in state["doc_chunks"]:
                    context_parts.append(f"[{c.get('filename')}, Page {c.get('page')}]: {c.get('text')}")

            if state["web_results"]:
                context_parts.append("--- WEB CONTEXT ---")
                for w in state["web_results"]:
                    context_parts.append(f"[{w.get('title')}]: {w.get('snippet')}")

            if state["memory_context"]:
                context_parts.append("--- CONVERSATION HISTORY ---")
                for m in state["memory_context"]:
                    context_parts.append(f"User: {m.get('user_message')}\nAssistant: {m.get('assistant_response')}")

            state["compiled_context"] = "\n\n".join(context_parts)

            # 5. LLM Generator Node (with explicit length and citation mode prompts)
            if mode == "report":
                system_prompt = (
                    "You are a Senior Academic Researcher. Write a formal, rigorous, comprehensive research report "
                    "strictly between 800 and 1000 words. Divide the report into well-structured Markdown sections: "
                    "# Title, ## Executive Summary, ## Introduction & Background, ## Literature Review & Methodology, "
                    "## Detailed Analysis & Findings, ## Critical Discussion, ## Conclusion. "
                    "Ground your analysis strictly in the provided research context and include less than 10 citations."
                )
            elif mode == "slides":
                system_prompt = (
                    "You are an Executive Academic Presenter. Generate detailed presentation slide deck content. "
                    "Provide at least 10 slides. Each slide MUST contain 80 to 100 words of comprehensive bullet points "
                    "and explanatory narratives. Keep total citations across all slides under 5."
                )
            else:
                system_prompt = (
                    "You are an Advanced AI Research Assistant. Provide a detailed, accurate research response "
                    "strictly between 200 and 300 words. Ground your answer in the provided context and include "
                    "less than 10 citations with reference tags [1], [2], etc."
                )

            gen_prompt = (
                f"MODE: {mode.upper()}\n"
                f"Question / Topic: {state['question']}\n\n"
                f"Research Context:\n{state['compiled_context']}\n\n"
                f"Citations Available:\n" + "\n".join(state['citations']) + "\n\n"
                "Formulate your complete answer strictly following the required length, structure, and citation format."
            )
            state["candidate_answer"] = self.llm.generate(gen_prompt, system_instruction=system_prompt)

            # 6. Critic Agent Node
            critic_res = self.critic_agent.evaluate(
                question=state["question"],
                response=state["candidate_answer"],
                context=state["compiled_context"]
            )
            state["critic_is_good"] = critic_res["is_good"]
            state["critic_feedback"] = critic_res["feedback"]

            # 7. Check Decision Good / Retry
            if state["critic_is_good"] or state["retry_count"] >= max_retries:
                state["final_answer"] = state["candidate_answer"]
                break

            state["retry_count"] += 1
            logger.info(f"Critic rejected candidate answer. Retrying workflow (Attempt {state['retry_count']})")

        return {
            "answer": state["final_answer"],
            "citations": state["citations"],
            "sources": state["sources"],
            "plan": state["plan_summary"],
            "retries": state["retry_count"]
        }


# Global workflow instance
workflow = ResearchAgentWorkflow()
