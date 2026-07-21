from typing import Dict, Any, List
from agents.graph import workflow
from sqlalchemy.orm import Session


def generate_presentation_slides(topic: str, document_id: str = None, user_id: str = None, db: Session = None) -> Dict[str, Any]:
    """
    Generates structured slide presentation JSON object based on research agent analysis.
    """
    agent_output = workflow.run(
        question=f"Generate key bullet points and presentation slide topics for: {topic}",
        user_id=user_id,
        document_id=document_id,
        db=db
    )

    slides: List[Dict[str, Any]] = [
        {
            "slide_number": 1,
            "title": topic,
            "subtitle": "AI Research Assistant Synthesis",
            "bullets": ["Automated Multi-Agent Literature Review", "Fact-Checked Context & Citations"]
        },
        {
            "slide_number": 2,
            "title": "Executive Overview",
            "bullets": [agent_output.get("answer")[:200] + "..."]
        },
        {
            "slide_number": 3,
            "title": "Key Findings & Evidence",
            "bullets": [
                line.strip("- *")
                for line in agent_output.get("answer", "").split("\n")
                if line.strip()
            ][:4]
        },
        {
            "slide_number": 4,
            "title": "References & Citations",
            "bullets": agent_output.get("citations", ["Uploaded Document Context"])[:5]
        }
    ]

    return {
        "title": f"Presentation Deck: {topic}",
        "slides": slides,
        "total_slides": len(slides)
    }
