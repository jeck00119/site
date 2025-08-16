import asyncio
import re
from asyncio import sleep
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File, Body
from pydantic import BaseModel, field_validator
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, handle_route_errors, handle_websocket_errors, create_crud_error_handlers
from api.route_utils import RouteHelper, require_authentication
from api.ws_connection_manager import ConnectionManager
from repo.repositories import AlgorithmsRepository, CustomComponentsRepository
from repo.repository_exceptions import UidNotUnique, UidNotFound
from services.algorithms.algorithms_models import AlgorithmModel
from services.algorithms.algorithms_service import AlgorithmsService
from services.algorithms.basic.basic_algorithms_service import BasicAlgorithmsService
from services.algorithms.basic.models.data_representation import NumpyType
from services.authorization.authorization import get_current_user
from services.camera_calibration.camera_calibration_service import CameraCalibrationService
from services.custom_components.custom_components_model import CustomComponentModel
from services.image_source.image_source_service import ImageSourceService
from services.image_source.load_image_service import LoadImageService
from services.services_exceptions import NoLiveAlgSet, NoLiveFrameSet
from src.utils import frame_to_base64

router = APIRouter(
    tags=["algorithm"],
    prefix="/algorithm"
)


class Reference(BaseModel):
    alg_type: str
    alg_parameters: dict


class BasicAttribute(BaseModel):
    idx: int
    name: str
    value: Any

    @field_validator('name')
    @classmethod
    def snake_case(cls, v):
        v = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', v)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', v).lower()


class DataBlocks(BaseModel):
    blockIndex: list
    outputIndex: list


class AlgorithmBlocks(BaseModel):
    types: list
    data_blocks: list


class Field(BaseModel):
    key: str
    value: Any

    @field_validator('key')
    @classmethod
    def snake_case(cls, v):
        print(f"DEBUG: Field validator converting '{v}' to snake_case")
        v_snake = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', v)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', v_snake).lower()
        print(f"DEBUG: Field validator result: '{result}'")
        return result


@router.get("")
@handle_route_errors("list", "Algorithm")
async def list_configured_algorithms(
        _: dict = Depends(require_authentication("list algorithms")),
        algorithms_repository: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository))
) -> List[AlgorithmModel]:
    algorithms = RouteHelper.list_entities(algorithms_repository, "Algorithm")
    # Return full algorithm models instead of just uid/name to include type and parameters
    return [AlgorithmModel(**algorithm) for algorithm in algorithms]


@router.get("/types")
@handle_route_errors("list types", "Algorithm")
async def list_algorithms_types(
        _: dict = Depends(require_authentication("list algorithm types")),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> List[str]:
    result = algorithm_service.list_algorithms_types()
    return RouteHelper.create_success_response("Algorithm types retrieved successfully", result)


@router.get("/basic/types")
@handle_route_errors("list basic types", "Algorithm")
async def list_basic_algorithm_types(
        _: dict = Depends(require_authentication("list basic algorithm types")),
        basic_algorithms_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, Any]:
    result = basic_algorithms_service.list_algorithm_types_and_params()
    return RouteHelper.create_success_response("Basic algorithm types retrieved successfully", result)


@router.get("/reference/types")
@handle_route_errors("list reference types", "Algorithm")
async def list_reference_algorithm_types(
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    result = algorithm_service.list_reference_algorithms_types()
    return RouteHelper.create_success_response("Reference algorithm types retrieved successfully", result)


@router.get("/types/{algorithm_type}")
@handle_route_errors("get parameter UI", "Algorithm", "algorithm_type")
async def get_alg_param_ui(
        algorithm_type: str,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    base_alg_type = {
        'parameters': algorithm_service.get_ui_from_type(algorithm_type),
    }
    return RouteHelper.create_success_response(base_alg_type)


@router.get("/basic/types/{algorithm_type}")
@handle_route_errors("get basic parameter UI", "Algorithm", "algorithm_type")
async def get_basic_alg_param_ui(
        algorithm_type: str,
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, Any]:
    base_alg_type = {
        'parameters': basic_algorithm_service.get_ui_from_type(algorithm_type),
    }
    return RouteHelper.create_success_response(base_alg_type)


@router.get("/reference/types/{algorithm_type}")
@handle_route_errors("get reference parameter UI", "Algorithm", "algorithm_type")
async def get_ref_alg_param_ui(
        algorithm_type: str,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    # Handle both single and comma-separated algorithm types
    if ',' in algorithm_type:
        # Multiple algorithm types - return parameters for the first valid one
        # or combine them as needed
        algorithm_types = [t.strip() for t in algorithm_type.split(',')]
        for algo_type in algorithm_types:
            try:
                result = {
                    'parameters': algorithm_service.get_ui_from_reference_type(algo_type)
                }
                return RouteHelper.create_success_response(result)
            except:
                continue
        # If none worked, return empty parameters
        return RouteHelper.create_success_response({'parameters': []})
    else:
        # Single algorithm type
        result = {
            'parameters': algorithm_service.get_ui_from_reference_type(algorithm_type)
        }
        return RouteHelper.create_success_response(result)


@router.get("/{algorithm_uid}")
@handle_route_errors("retrieve", "Algorithm", "algorithm_uid")
async def get_algorithm(
        algorithm_uid: str,
        algorithms_repository: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository))
) -> AlgorithmModel:
    entity_data = RouteHelper.get_entity_by_id(
        algorithms_repository,
        algorithm_uid,
        "Algorithm"
    )
    return AlgorithmModel(**entity_data)


@router.post("")
@handle_route_errors("create", "Algorithm", success_status=201)
async def post_algorithm(
        algorithm: AlgorithmModel,
        _: dict = Depends(require_authentication),
        algorithms_repository: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository))
) -> Dict[str, str]:
    return RouteHelper.create_entity(
        algorithms_repository,
        algorithm,
        "Algorithm"
    )


@router.put("/{algorithm_uid}")
@handle_route_errors("update", "Algorithm", "algorithm_uid")
async def put_algorithm(
        algorithm_uid: str,
        algorithm: AlgorithmModel,
        _: dict = Depends(require_authentication),
        algorithms_repository: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository))
) -> Dict[str, str]:
    return RouteHelper.update_entity(
        algorithms_repository,
        algorithm,
        "Algorithm"
    )


@router.delete("/{algorithm_uid}")
@handle_route_errors("delete", "Algorithm", "algorithm_uid")
async def delete_algorithm(
        algorithm_uid: str,
        _: dict = Depends(require_authentication),
        algorithms_repository: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository))
) -> Dict[str, str]:
    return RouteHelper.delete_entity(
        algorithms_repository,
        algorithm_uid,
        "Algorithm"
    )


@router.get("/__API__/set_live_algorithm/{algorithm_type}")
@handle_route_errors("set live algorithm", "Algorithm", "algorithm_type")
async def set_live_algorithm(
        algorithm_type: str,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    algorithm_service.set_live_algorithm(algorithm_type)
    base_alg_type = {
        'parameters': algorithm_service.get_ui_from_type(algorithm_type),
        'alg_model': algorithm_service.get_model_from_type(algorithm_type).model_dump()
    }
    return RouteHelper.create_success_response(base_alg_type)


@router.get("/__API__/set_live_algorithm_reference/{reference_uid}")
@handle_route_errors("set live algorithm reference", "Algorithm", "reference_uid")
async def set_live_algorithm_reference_repository(
        reference_uid: str,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.set_live_algorithm_reference_repo(reference_uid)
    return RouteHelper.create_success_response("Live algorithm reference set successfully")


@router.post("/__API__/set_live_algorithm_reference_dict")
@handle_route_errors("set live algorithm reference dictionary", "Algorithm")
async def set_live_algorithm_reference_dict(
        reference_algorithm: Reference,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.set_live_algorithm_reference_dict(
        reference_algorithm.alg_type,
        reference_algorithm.alg_parameters
    )
    return RouteHelper.create_success_response("Live algorithm reference dictionary set successfully")


@router.get("/__API__/set_reference_algorithm/{algorithm_type}")
@handle_route_errors("set reference algorithm", "Algorithm", "algorithm_type")
async def set_reference_algorithm(
        algorithm_type: str,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.set_reference_algorithm(algorithm_type)
    return RouteHelper.create_success_response("Reference algorithm set successfully")


@router.get("/__API__/set_live_algorithm_reference")
@handle_route_errors("set live algorithm reference", "Algorithm")
async def set_live_algorithm_reference(
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.set_live_algorithm_reference()
    return RouteHelper.create_success_response("Live algorithm reference set successfully")


@router.get("/__API__/reset_live_algorithm_reference")
@handle_route_errors("reset live algorithm reference", "Algorithm")
async def reset_live_algorithm_reference(
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.reset_reference_algorithm()
    return RouteHelper.create_success_response("Live algorithm reference reset successfully")


@router.post("/__API__/basic/edit_live_algorithm_field")
@handle_route_errors("edit basic live algorithm field", "Algorithm")
async def set_basic_live_algorithm(
        data: BasicAttribute,
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, str]:
    basic_algorithm_service.edit_live_algorithm_field(data.idx, data.name, data.value)
    return RouteHelper.create_success_response("Basic live algorithm field edited successfully")


@router.get("/__API__/basic/edit_live_algorithm/{custom_component_uid}")
@handle_route_errors("set basic live algorithm repository", "Algorithm", "custom_component_uid")
async def set_basic_live_algorithm_repository(
        custom_component_uid: str,
        custom_components_repository: CustomComponentsRepository = Depends(get_service_by_type(CustomComponentsRepository)),
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, str]:
    component_dict = custom_components_repository.read_id(custom_component_uid)
    component = CustomComponentModel(**component_dict)

    if component:
        for idx, algorithm in enumerate(component.algorithms):
            basic_algorithm_service.edit_live_algorithm(idx, algorithm['parameters'])
    
    return RouteHelper.create_success_response("Basic live algorithm repository updated successfully")


@router.post("/__API__/basic/edit_live_algorithm")
@handle_route_errors("set basic live algorithm from dict", "Algorithm")
async def set_basic_live_algorithm_from_dict(
        data: List[Dict[str, Any]],
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, str]:
    for idx, algorithm in enumerate(data):
        basic_algorithm_service.edit_live_algorithm(idx, algorithm)
    return RouteHelper.create_success_response("Basic live algorithm updated from dictionary successfully")


@router.post("/__API__/basic/set_live_algorithm")
@handle_route_errors("set live compound algorithm", "Algorithm")
async def set_live_compound_algorithm(
        blocks: AlgorithmBlocks,
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService))
) -> Dict[str, str]:
    basic_algorithm_service.set_algorithm_types(blocks.types)
    basic_algorithm_service.set_blocks(blocks.data_blocks)
    basic_algorithm_service.set_live_algorithm()
    return RouteHelper.create_success_response("Live compound algorithm set successfully")


@router.post("/__API__/edit_live_algorithm")
@handle_route_errors("edit live algorithm", "Algorithm")
async def edit_live_algorithm(
        algorithm: Field,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.edit_live_algorithm(algorithm.key, algorithm.value)
    return RouteHelper.create_success_response("Live algorithm edited successfully")


@router.post("/__API__/edit_reference_algorithm")
@handle_route_errors("edit reference algorithm", "Algorithm")
@handle_route_errors("edit reference algorithm", "Algorithm")
async def edit_reference_algorithm(
        field: Field,
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, str]:
    algorithm_service.edit_reference_algorithm(field.key, field.value)
    return RouteHelper.create_success_response("Reference algorithm edited successfully")


@router.post("/__API__/upload_resource")
@handle_route_errors("upload resource", "Algorithm")
async def upload_resource(
        file: UploadFile = File(...),
        path: str = Form(...)
) -> Dict[str, str]:
    with open(f"{path}/{file.filename}", 'wb') as f:
        while True:
            chunk = await file.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)
    
    return RouteHelper.create_success_response("Resource uploaded successfully")


@router.get("/__API__/process_live_algorithm")
async def process_live_component_image(
        load_image_service: LoadImageService = Depends(get_service_by_type(LoadImageService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    try:
        frame = load_image_service.get_frame()
        algorithm = algorithm_service.get_live_algorithm()

        def alg_lambda(): return algorithm.execute(frame)

        loop = asyncio.get_running_loop()
        alg_result = await loop.run_in_executor(None, alg_lambda)
        
        proc_frames = []
        for image in alg_result.debugImages:
            proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))
        
        result = {
            'frame': proc_frames,
            'data': alg_result.data
        }
        return RouteHelper.create_success_response(result)
    except (NoLiveAlgSet, NoLiveFrameSet) as e:
        raise create_error_response(
            operation="process live algorithm",
            entity_type="Algorithm",
            exception=e
        )
    except Exception as e:
        raise create_error_response(
            operation="process live algorithm",
            entity_type="Algorithm",
            exception=e
        )


@router.get("/__API__/process_reference_algorithm")
async def process_reference_algorithm_image(
        load_image_service: LoadImageService = Depends(get_service_by_type(LoadImageService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
) -> Dict[str, Any]:
    try:
        frame = load_image_service.get_frame()
        algorithm = algorithm_service.get_reference_algorithm()
        alg_result = algorithm.execute(frame)
        
        proc_frames = []
        for image in alg_result.debugImages:
            proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))
        
        result = {
            'frame': proc_frames,
            'data': alg_result.data,
            'reference': alg_result.referencePoints
        }
        return RouteHelper.create_success_response(result)
    except (NoLiveAlgSet, NoLiveFrameSet) as e:
        raise create_error_response(
            operation="process reference algorithm",
            entity_type="Algorithm",
            exception=e
        )
    except Exception as e:
        raise create_error_response(
            operation="process reference algorithm",
            entity_type="Algorithm",
            exception=e
        )


@router.get("/__API__/process_live_algorithm/{image_source_uid}")
async def process_live_component(
        image_source_uid: str,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
) -> Dict[str, Any]:
    try:
        frame = image_source_service.get_frame(image_source_uid)
        calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

        if calibration_uid:
            frame = camera_calibration_service.undistort_image(frame, calibration_uid)

        algorithm = algorithm_service.get_live_algorithm()
        alg_result = algorithm.execute(frame)
        
        proc_frames = []
        for image in alg_result.debugImages:
            proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))
        
        result = {
            'frame': proc_frames,
            'data': alg_result.data,
            'reference': alg_result.referencePoints
        }
        return RouteHelper.create_success_response(result)
    except (NoLiveAlgSet, NoLiveFrameSet) as e:
        raise create_error_response(
            operation="process live algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except UidNotFound as e:
        raise create_error_response(
            operation="process live algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except Exception as e:
        raise create_error_response(
            operation="process live algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )


@router.get("/__API__/process_reference_algorithm/{image_source_uid}")
async def process_reference_algorithm_img_src(
        image_source_uid: str,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
) -> Dict[str, Any]:
    try:
        frame = image_source_service.get_frame(image_source_uid)
        calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

        if calibration_uid:
            frame = camera_calibration_service.undistort_image(frame, calibration_uid)

        algorithm = algorithm_service.get_reference_algorithm()
        alg_result = algorithm.execute(frame)
        
        proc_frames = []
        for image in alg_result.debugImages:
            proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))
        
        result = {
            'frame': proc_frames,
            'data': alg_result.data,
            'reference': alg_result.referencePoints
        }
        return RouteHelper.create_success_response(result)
    except (NoLiveAlgSet, NoLiveFrameSet) as e:
        raise create_error_response(
            operation="process reference algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except UidNotFound as e:
        raise create_error_response(
            operation="process reference algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except Exception as e:
        raise create_error_response(
            operation="process reference algorithm with image source",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )


@router.get("/__API__/basic/process_live_algorithm/{image_source_uid}")
async def process_live_compound_algorithm(
        image_source_uid: str,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
) -> Dict[str, Any]:
    try:
        frame = image_source_service.get_frame(image_source_uid)
        calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

        if calibration_uid:
            frame = camera_calibration_service.undistort_image(frame, calibration_uid)

        algorithm = basic_algorithm_service.get_live_algorithm()
        basic_algorithm_service.set_input_frame(frame)
        alg_result = algorithm.execute()

        results = basic_algorithm_service.get_compound_result()

        if isinstance(alg_result.outs[0], NumpyType):
            out_image = alg_result.outs[0].value()
        else:
            out_image = np.zeros(shape=(128, 128), dtype=np.uint8)
        
        result = {
            'frame': frame_to_base64(out_image, quality=80),
            'results': results,
            'data': ''
        }
        return RouteHelper.create_success_response(result)
    except (NoLiveAlgSet, NoLiveFrameSet) as e:
        raise create_error_response(
            operation="process live compound algorithm",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except UidNotFound as e:
        raise create_error_response(
            operation="process live compound algorithm",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )
    except Exception as e:
        raise create_error_response(
            operation="process live compound algorithm",
            entity_type="Algorithm",
            entity_id=image_source_uid,
            exception=e
        )


@router.post("/__API__/set_static_image")
@handle_route_errors("set static image", "Algorithm")
async def set_static_image(
        encoded_image: str = Body(...),
        load_image_service: LoadImageService = Depends(get_service_by_type(LoadImageService))
) -> Dict[str, str]:
    load_image_service.set_encoded_image(encoded_image)
    load_image_service.load_image()
    return RouteHelper.create_success_response("Static image set successfully")


manager = ConnectionManager()


@router.websocket("/live_algorithm_result/{image_source_uid}/{ws_uid}/ws")
async def websocket_algorithm_img_src(
        websocket: WebSocket,
        image_source_uid,
        ws_uid,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                if data["command"] == "set":
                    algorithm_service.edit_live_algorithm(data["key"], data["value"])

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass

            try:
                frame = image_source_service.get_frame(image_source_uid)

                calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

                if calibration_uid:
                    frame = camera_calibration_service.undistort_image(frame, calibration_uid)

                algorithm = algorithm_service.get_live_algorithm()
                alg_result = algorithm.execute(frame)
            except (NoLiveAlgSet, NoLiveFrameSet) as e:
                raise HTTPException(status_code=400, detail=f'{e}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'{e}')

            # proc_frame = frame_to_base64(alg_result.imageRoi).decode('utf-8')

            proc_frames = []

            for image in alg_result.debugImages:
                proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))

            ret = {'frame': proc_frames,
                   'placeholder': ''}

            await websocket.send_json(ret)
            await sleep(0.3)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)


@router.websocket("/live_algorithm_result/{ws_uid}/ws")
async def websocket_algorithm_static(
        websocket: WebSocket,
        ws_uid,
        load_image_service: LoadImageService = Depends(get_service_by_type(LoadImageService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                if data["command"] == "set":
                    algorithm_service.edit_live_algorithm(data["key"], data["value"])

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass

            try:
                frame = load_image_service.get_frame()

                algorithm = algorithm_service.get_live_algorithm()
                alg_result = algorithm.execute(frame)
            except (NoLiveAlgSet, NoLiveFrameSet) as e:
                raise HTTPException(status_code=400, detail=f'{e}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'{e}')

            # proc_frame = frame_to_base64(alg_result.imageRoi).decode('utf-8')

            proc_frames = []

            for image in alg_result.debugImages:
                proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))

            ret = {
                'frame': proc_frames,
                'data': ''
            }

            await websocket.send_json(ret)
            await sleep(0.3)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)


@router.websocket("/live_reference/{image_source_uid}/{ws_uid}/ws")
async def websocket_reference_img_src(
        websocket: WebSocket,
        ws_uid,
        image_source_uid,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                if data["command"] == "set":
                    algorithm_service.edit_reference_algorithm(data["key"], data["value"])

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass

            try:
                frame = image_source_service.get_frame(image_source_uid)

                calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

                if calibration_uid:
                    frame = camera_calibration_service.undistort_image(frame, calibration_uid)

                algorithm = algorithm_service.get_reference_algorithm()
                alg_result = algorithm.execute(frame)
            except (NoLiveAlgSet, NoLiveFrameSet) as e:
                raise HTTPException(status_code=400, detail=f'{e}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'{e}')

            # proc_frame = frame_to_base64(alg_result.imageRoi).decode('utf-8')

            proc_frames = []

            for image in alg_result.debugImages:
                proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))

            ret = {
                'frame': proc_frames,
                'data': alg_result.data,
                'reference': alg_result.referencePoints
            }

            await websocket.send_json(ret)
            await sleep(0.3)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)


@router.websocket("/live_reference/{ws_uid}/ws")
async def websocket_reference_static(
        websocket: WebSocket,
        ws_uid,
        load_image_service: LoadImageService = Depends(get_service_by_type(LoadImageService)),
        algorithm_service: AlgorithmsService = Depends(get_service_by_type(AlgorithmsService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                if data["command"] == "set":
                    algorithm_service.edit_reference_algorithm(data["key"], data["value"])

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass

            try:
                frame = load_image_service.get_frame()

                algorithm = algorithm_service.get_reference_algorithm()
                alg_result = algorithm.execute(frame)
            except (NoLiveAlgSet, NoLiveFrameSet) as e:
                raise HTTPException(status_code=400, detail=f'{e}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'{e}')

            # proc_frame = frame_to_base64(alg_result.imageRoi).decode('utf-8')

            proc_frames = []

            for image in alg_result.debugImages:
                proc_frames.append(frame_to_base64(image, quality=80).decode('utf-8'))

            ret = {
                'frame': proc_frames,
                'data': alg_result.data,
                'reference': alg_result.referencePoints
            }

            await websocket.send_json(ret)
            await sleep(0.3)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)


@router.websocket("/basic/live_algorithm_result/{image_source_uid}/{ws_uid}/ws")
async def websocket_basic_algorithm_img_src(
        websocket: WebSocket,
        ws_uid,
        image_source_uid,
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        basic_algorithm_service: BasicAlgorithmsService = Depends(get_service_by_type(BasicAlgorithmsService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                if data["command"] == "set":
                    basic_algorithm_service.edit_live_algorithm_field(data["idx"], data["key"], data["value"])

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass

            try:
                frame = image_source_service.get_frame(image_source_uid)

                calibration_uid = image_source_service.get_calibration_uid(image_source_uid)

                if calibration_uid:
                    frame = camera_calibration_service.undistort_image(frame, calibration_uid)

                algorithm = basic_algorithm_service.get_live_algorithm()

                basic_algorithm_service.set_input_frame(frame)
                alg_result = algorithm.execute()

                results = basic_algorithm_service.get_compound_result(decode=True)

                if isinstance(alg_result.outs[0], NumpyType):
                    out_image = alg_result.outs[0].value()
                else:
                    out_image = np.zeros(shape=(128, 128), dtype=np.uint8)
            except (NoLiveAlgSet, NoLiveFrameSet) as e:
                raise HTTPException(status_code=400, detail=f'{e}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'{e}')

            ret = {
                'frame': frame_to_base64(out_image, quality=80).decode('utf-8'),
                'results': results,
                'data': ''
            }

            await websocket.send_json(ret)
            await sleep(0.3)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)
