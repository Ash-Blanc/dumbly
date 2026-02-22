# backend/app/routers/stream.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services import stream_manager
import json

router = APIRouter(tags=["stream"])


@router.websocket("/ws/analysis/{analysis_id}")
async def analysis_stream(websocket: WebSocket, analysis_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await stream_manager.connect(websocket, analysis_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "cancel":
                from app.services import analysis_service
                analysis_service.cancel_analysis(analysis_id)
                await websocket.send_json({"type": "cancelled"})
                break

            elif message.get("action") == "select_paper":
                arxiv_id = message.get("arxiv_id")
                # Handle paper selection
                await stream_manager.emit(analysis_id, "paper_selected", {"arxiv_id": arxiv_id})

    except WebSocketDisconnect:
        stream_manager.disconnect(analysis_id)
