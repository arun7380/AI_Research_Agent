from typing import Dict, Any
from agents.graph import workflow
from sqlalchemy.orm import Session


def generate_research_report(topic: str, document_id: str = None, user_id: str = None, db: Session = None) -> Dict[str, Any]:
    """
    Generates a structured multi-page markdown research report on a topic using the multi-agent system.
    """
    agent_output = workflow.run(
        question=f"Generate a comprehensive, formal academic research report on: {topic}",
        user_id=user_id,
        document_id=document_id,
        db=db
    )

    report_markdown = (
        f"# Research Report: {topic}\n\n"
        f"## Executive Summary\n{agent_output.get('answer')[:400]}...\n\n"
        f"## Detailed Analysis & Findings\n{agent_output.get('answer')}\n\n"
        f"## Works Cited & References\n"
    )

    for cit in agent_output.get("citations", []):
        report_markdown += f"- {cit}\n"

    return {
        "title": f"Research Report: {topic}",
        "topic": topic,
        "content_markdown": report_markdown,
        "citations": agent_output.get("citations", []),
        "sources": agent_output.get("sources", [])
    }
