import logging

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from services.audio_service import AudioService

logger = logging.getLogger("logger")
audio_router = APIRouter(prefix="/audio")

# 创建一个全局的 AudioService 实例，这样可以保持录音状态
audio_service = AudioService()


# 开始录音
@audio_router.post("/start_recording")
async def start_recording(seat: str = Form(...), customer: str = Form(...), format: str = Form(...)) -> JSONResponse:
    audio_service.start_recording()
    return JSONResponse(
        content={"status": "Recording started", "format": format, "file": f"{seat}_{customer}.{format}"}
    )


# 暂停录音
@audio_router.post("/pause_recording")
async def pause_recording() -> JSONResponse:
    audio_service.pause_recording()
    return JSONResponse(content={"status": "Recording paused"})


# 恢复录音
@audio_router.post("/resume_recording")
async def resume_recording() -> JSONResponse:
    audio_service.resume_recording()
    return JSONResponse(content={"status": "Recording resumed"})


# 停止录音
@audio_router.post("/stop_recording")
async def stop_recording(seat: str = Form(...), customer: str = Form(...), format: str = Form(...)) -> JSONResponse:
    wav_path = audio_service.stop_recording(seat, customer, format)
    return JSONResponse(content={"status": "Recording stopped", "file": wav_path})

