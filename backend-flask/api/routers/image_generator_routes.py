import os
import pathlib
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends, UploadFile
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import ImageGeneratorRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.configurations.configurations_service import ConfigurationService
from services.image_generator.img_generator_model import ImageGeneratorModel

router = APIRouter(
    tags=["image_generator"],
    prefix="/image_generator"
)

generator_path = ''


@router.get("")
async def list_image_generators(
        image_generator_repository: ImageGeneratorRepository = Depends(get_service_by_type(ImageGeneratorRepository))
) -> JSONResponse:
    try:
        generators = RouteHelper.list_entities(
            image_generator_repository,
            "ImageGenerator"
        )
        return RouteHelper.create_success_response(generators)
    except Exception as e:
        raise create_error_response("list", "ImageGenerator", exception=e)


@router.get("/{image_generator_uid}")
async def get_image_generator(
        image_generator_uid: str,
        image_generator_repository: ImageGeneratorRepository = Depends(get_service_by_type(ImageGeneratorRepository))
) -> ImageGeneratorModel:
    try:
        res = RouteHelper.get_entity_by_id(
            image_generator_repository,
            image_generator_uid,
            "ImageGenerator"
        )
        return RouteHelper.create_success_response(ImageGeneratorModel(**res))
    except Exception as e:
        raise create_error_response("get", "ImageGenerator", entity_id=image_generator_uid, exception=e)


@router.post("")
async def post_image_generator(
        image_generator: ImageGeneratorModel,
        user: dict = Depends(require_authentication),
        image_generator_repository: ImageGeneratorRepository = Depends(get_service_by_type(ImageGeneratorRepository))
) -> JSONResponse:
    try:
        directory_path = pathlib.Path(__file__).parent.parent.parent.resolve()
        temp_path = generator_path.replace(str(directory_path), "")
        image_generator.dir_path = temp_path[1:]
        generators = image_generator_repository.read_all()
        paths = []

        for generator in generators:
            paths.append(generator['dir_path'])
        if image_generator.dir_path not in paths:
            RouteHelper.create_entity(
                image_generator_repository,
                image_generator,
                "ImageGenerator"
            )
        else:
            image_generator.dir_path = generator_path
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("create", "ImageGenerator", exception=e)


@router.put("/{image_generator_uid}")
async def put_image_generator(
        image_generator: ImageGeneratorModel,
        user: dict = Depends(require_authentication),
        image_generator_repository: ImageGeneratorRepository = Depends(get_service_by_type(ImageGeneratorRepository))
) -> JSONResponse:
    try:
        RouteHelper.update_entity(
            image_generator_repository,
            image_generator,
            "ImageGenerator"
        )
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("update", "ImageGenerator", entity_id=image_generator.uid, exception=e)


@router.delete("/{image_generator_uid}")
async def delete_image_generator(
        image_generator_uid: str,
        user: dict = Depends(require_authentication),
        image_generator_repository: ImageGeneratorRepository = Depends(get_service_by_type(ImageGeneratorRepository))
) -> JSONResponse:
    try:
        RouteHelper.delete_entity(
            image_generator_repository,
            image_generator_uid,
            "ImageGenerator"
        )
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("delete", "ImageGenerator", entity_id=image_generator_uid, exception=e)


@router.post("/upload_image_generator")
async def upload_files(
        file: UploadFile,
        user: dict = Depends(require_authentication),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
) -> JSONResponse:
    try:
        current_config = configuration_service.get_current_configuration_name()
        if current_config:

            directory = file.filename.split("/")[0]
            filename = file.filename.split("/")[1]

            path = pathlib.Path(
                __file__).parent.parent.parent.resolve() / 'config_db' / current_config / 'images' / directory
            file_path = path / filename
            if not os.path.exists(path):
                os.makedirs(path)

            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)

            global generator_path
            generator_path = str(path)
        
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("upload", "ImageGenerator", exception=e)
