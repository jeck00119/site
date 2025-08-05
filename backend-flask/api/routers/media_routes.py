from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import AudioEventsRepository
from services.authorization.authorization import get_current_user
from services.media.audio_model import AudioModel
from services.media.pygame_audio_service import PygameAudioService

router = APIRouter(
    tags=['media'],
    prefix='/media'
)


@router.get('/events')
async def get_events(
        audio_service: PygameAudioService = Depends(get_service_by_type(PygameAudioService))
) -> List[Dict]:
    try:
        events = audio_service.get_events()
        # Convert list of strings to list of dictionaries for security middleware compatibility
        return [{"name": event} for event in events]
    except Exception as e:
        raise create_error_response(
            operation="retrieve", 
            entity_type="Media", 
            exception=e
        )


@router.get('/files')
async def get_media_files(
        audio_service: PygameAudioService = Depends(get_service_by_type(PygameAudioService))
) -> Dict[str, Any]:
    try:
        files = audio_service.get_media_list()
        return {"files": files, "count": len(files)}
    except Exception as e:
        raise create_error_response(
            operation="retrieve", 
            entity_type="Media", 
            exception=e
        )


@router.get('/channels')
async def get_channels(
        audio_service: PygameAudioService = Depends(get_service_by_type(PygameAudioService))
) -> Dict[str, Any]:
    try:
        channels = audio_service.get_number_of_channels()
        return {"channels": list(range(channels)), "count": channels}
    except Exception as e:
        raise create_error_response(
            operation="retrieve", 
            entity_type="Media", 
            exception=e
        )


@router.post('/channel')
async def add_media_channel(
        _: dict = Depends(require_authentication("add media channel")),
        audio_service: PygameAudioService = Depends(get_service_by_type(PygameAudioService))
) -> Dict[str, Any]:
    try:
        audio_service.add_new_channel()
        new_channel_count = audio_service.get_number_of_channels()
        return RouteHelper.create_success_response(
            "Audio channel added successfully",
            {"total_channels": new_channel_count},
            status.HTTP_201_CREATED
        )
    except Exception as e:
        raise create_error_response(
            operation="create", 
            entity_type="Media", 
            exception=e
        )


@router.post('/add_event')
async def add_event(
        audio: AudioModel,
        _: dict = Depends(require_authentication("add media event")),
        audio_repository: AudioEventsRepository = Depends(get_service_by_type(AudioEventsRepository))
) -> Dict[str, str]:
    try:
        audio_dict = {
            audio.name: {
                "path": audio.path,
                "timeout": audio.timeout,
                "channel": audio.channel,
                "priority": audio.priority,
                "volume": audio.volume
            }
        }
        
        audio_repository.update(audio_dict)
        
        return RouteHelper.create_success_response(
            f"Media event '{audio.name}' added successfully"
        )
    except Exception as e:
        raise create_error_response(
            operation="create", 
            entity_type="Media", 
            exception=e
        )
