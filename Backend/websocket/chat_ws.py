import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from agents.graph import workflow

router = APIRouter(tags=["WebSocket Realtime Agent Console"])


@router.websocket("/ws/chat")
async def websocket_chat_agent(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            question = payload.get("question", "")
            document_id = payload.get("document_id")

            # Stream Agent Step 1: Planner
            await websocket.send_json({"step": "planner", "message": "Planner Agent decomposing question..."})

            # Stream Agent Step 2: Parallel Workers
            await websocket.send_json({"step": "workers", "message": "Executing Research, Web, Memory & Citation Agents..."})

            # Stream Agent Step 3: Context & LLM Generation
            await websocket.send_json({"step": "llm", "message": "Context Builder & LLM Generator synthesizing answer..."})

            # Stream Agent Step 4: Critic Agent
            await websocket.send_json({"step": "critic", "message": "Critic Agent evaluating factual grounding..."})

            res = workflow.run(question=question, document_id=document_id)

            await websocket.send_json({
                "step": "completed",
                "answer": res["answer"],
                "citations": res["citations"],
                "sources": res["sources"]
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"step": "error", "message": str(e)})
