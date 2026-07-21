from typing import Dict, Any
from agents.graph import workflow
from sqlalchemy.orm import Session


def generate_research_report(topic: str, document_id: str = None, user_id: str = None, db: Session = None) -> Dict[str, Any]:
    """
    Generates a structured 800 to 1000 word academic markdown research report using the multi-agent system.
    Citations are capped at < 10 with clickable hyperlinks.
    """
    agent_output = workflow.run(
        question=f"Generate a comprehensive, formal academic research report of 800 to 1000 words on: {topic}",
        user_id=user_id,
        document_id=document_id,
        db=db,
        mode="report"
    )

    answer_text = agent_output.get("answer", "")
    citations = agent_output.get("citations", [])[:9]  # strictly < 10

    # Ensure structured markdown formatting with references
    report_markdown = answer_text

    if citations and "## Works Cited & References" not in report_markdown and "## References" not in report_markdown:
        report_markdown += "\n\n## Works Cited & References\n"
        for cit in citations:
            report_markdown += f"- {cit}\n"

    return {
        "title": f"Academic Research Report: {topic}",
        "topic": topic,
        "content_markdown": report_markdown,
        "citations": citations,
        "sources": agent_output.get("sources", [])[:9]
    }

