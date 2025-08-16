import base64
import io
import os.path
import shutil
import tempfile
import zipfile
from os import listdir
from os.path import isfile, join
from typing import List

import aiofiles as aiofiles
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from starlette import status
from starlette.responses import JSONResponse
from ultralytics import YOLO

from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication

router = APIRouter(
    tags=['annotation'],
    prefix='/annotation'
)


def annotate_image(model, image: bytes, mode: str = "detection") -> str:
    pil_image = Image.open(io.BytesIO(image))
    results = model(pil_image)

    result_str = ""

    for result in results:
        if mode == "detection":
            classes = result.boxes.cls.numpy()
            norm_coords = result.boxes.xyxyn.numpy()

            if classes is not None:
                for i in range(classes.shape[0]):
                    result_str += str(int(classes[i])) + " "

                    val = norm_coords[i]

                    result_str += str(val[0]) + " " + str(val[1]) + " " + str(val[2]) + " " + str(val[1]) + " " + str(
                        val[2]) + " " + str(val[3]) + " " + str(val[0]) + " " + str(val[1]) + "\n"
        elif mode == "segmentation":
            classes = result.boxes.cls.numpy()
            masks = result.masks.xyn

            if masks is not None:
                for i in range(masks.shape[0]):
                    mask = masks[i]
                    result_str += str(int(classes[i])) + " "

                    for j in range(mask.shape[0]):
                        if j == mask.shape[0] - 1:
                            result_str += str(mask[j][0]) + " " + str(mask[j][1])
                        else:
                            result_str += str(mask[j][0]) + " " + str(mask[j][1]) + " "

                    result += "\n"
        else:
            classes = result.obb.cls.numpy()
            oriented_bbs = result.obb.xyxyxyxyn.numpy()

            if oriented_bbs is not None:
                for i in range(oriented_bbs.shape[0]):
                    bb = oriented_bbs[i]
                    result_str += str(int(classes[i])) + " "

                    for j in range(bb.shape[0]):
                        if j == bb.shape[0] - 1:
                            result_str += str(bb[j][0]) + " " + str(bb[j][1])
                        else:
                            result_str += str(bb[j][0]) + " " + str(bb[j][1]) + " "

                    result += "\n"

        return result_str


@router.get("/models")
async def get_available_models() -> List[str]:
    try:
        files = [f for f in listdir("assets/yolov8") if isfile(join("assets/yolov8", f))]
        return RouteHelper.create_success_response("Models retrieved successfully", files)
    except Exception as e:
        raise create_error_response("list", "Annotation", exception=e)


@router.post("/annotate")
async def annotate(
        background_tasks: BackgroundTasks,
        files: List[UploadFile] = File(...),
        model: str = Form(...),
        mode: str = Form(...),
        user: dict = Depends(require_authentication)
) -> StreamingResponse:

    # file_data = await request.json()
    #
    # if "model" not in file_data or "images" not in file_data:
    #     raise HTTPException(status_code=400, detail="Missing 'model_name' or 'images' in request body")
    # if not isinstance(file_data['images'], dict):
    #     raise HTTPException(status_code=400, detail="'images' must be a dict")
    # if not isinstance(file_data['model'], str):
    #     raise HTTPException(status_code=400, detail="'model' must be a string")

    temp_dir = tempfile.mkdtemp()
    images_dir = os.path.join(temp_dir, 'images')
    labels_dir = os.path.join(temp_dir, 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    try:
        yolo_model = YOLO(f"assets/yolov8/{model}")

        for file in files:
            contents = await file.read()
            img_str = base64.b64encode(contents).decode('utf-8')
            img_data = base64.b64decode(img_str)
            img_path = os.path.join(images_dir, file.filename)

            with open(img_path, 'wb') as f:
                f.write(img_data)

            res_str = annotate_image(yolo_model, img_data, mode=mode.lower())

            label_filename = file.filename.rsplit('.', 1)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_filename)
            with open(label_path, 'w') as f:
                # Write labels in YOLOv8 format
                f.write(res_str)

        zip_filename = 'output.zip'
        zip_path = os.path.join(temp_dir, zip_filename)
        zip_buffer = io.BytesIO()
        # with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        #     for folder_name in ['images', 'labels']:
        #         folder_path = os.path.join(temp_dir, folder_name)
        #         for root, _, files in os.walk(folder_path):
        #             for file in files:
        #                 file_path = os.path.join(root, file)
        #                 zip_file.write(file_path, arcname=file)
        # zip_buffer.seek(0)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_name in ['images', 'labels']:
                folder_path = os.path.join(temp_dir, folder_name)
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=temp_dir)
                        zipf.write(file_path, arcname)

        # Step 5: Return the zip file as a response
        async def iterfile():
            async with aiofiles.open(zip_path, mode="rb") as file_like:
                while True:
                    chunk = await file_like.read(1024 * 1024)  # Read in 1MB chunks
                    if not chunk:
                        break
                    yield chunk

        # shutil.rmtree(temp_dir)
        background_tasks.add_task(shutil.rmtree, temp_dir)

        return StreamingResponse(iterfile(), media_type="application/x-zip-compressed", headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        })
    except Exception as e:
        raise create_error_response("annotate", "Annotation", exception=e)


@router.post("/upload_model")
async def upload_model(
        file: UploadFile = File(...),
        user: dict = Depends(require_authentication)
) -> JSONResponse:
    try:
        with open(f"assets/yolov8/{file.filename}", 'wb') as f:
            while True:
                chunk = await file.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)

        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("upload", "Annotation", exception=e)