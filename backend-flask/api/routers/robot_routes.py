import asyncio

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from tinydb import Query

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, validate_authentication, handle_cnc_operation_errors
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import RobotRepository, RobotPositionsRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.port_manager.port_manager import PortManager
from services.robot.dependencies.ultra_arm import UltraArm
from services.robot.robot_models import RobotModel, XArmModel, UltraArmModel, RobotPositionsModel
from services.robot.robot_service import RobotService

router = APIRouter(
    tags=["robot"],
    prefix="/robot"
)


@router.get("")
async def get_robots(
        robot_repository: RobotRepository = Depends(get_service_by_type(RobotRepository)),
):
    try:
        return RouteHelper.list_entities(robot_repository, "Robot")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="list_robots",
            entity_type="Robot",
            exception=e
        )


@router.get("/robot_types")
async def get_robot_types(robot_service: RobotService = Depends(get_service_by_type(RobotService))):
    return robot_service.get_available_types()


@router.get("/ultra_arm_ports")
async def get_ultra_arm_ports(
        port_manager: PortManager = Depends(get_service_by_type(PortManager)),
):
    try:
        return await port_manager.get_available_ports_ultra_arm()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_ultra_arm_ports",
            entity_type="Port",
            exception=e
        )


@router.get("/{robot_uid}")
async def get_robot(
        robot_uid: str,
        robot_repository: RobotRepository = Depends(get_service_by_type(RobotRepository)),
):
    try:
        res = RouteHelper.get_entity_by_id(robot_repository, robot_uid, "Robot")

        if res["type"] == "xArm":
            res = XArmModel(**res)
        elif res["type"] == "ultraArm":
            res = UltraArm(**res)
        else:
            res = None
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_robot",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/save")
async def post_robots(
        robot_list: list,
        user: dict = Depends(require_authentication("save robots")),
        robot_repository: RobotRepository = Depends(get_service_by_type(RobotRepository)),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        robot_models = []

        for robot in robot_list:
            if robot["type"] == "xArm":
                model = XArmModel(**robot)
            elif robot["type"] == "ultraArm":
                model = UltraArmModel(**robot)
            else:
                model = RobotModel(**robot)
            robot_models.append(model)

        add, update, delete = robot_service.update_robots(robot_models)

        for robot_model in robot_models:
            if robot_model.uid in add:
                robot_repository.create(robot_model)
            if robot_model.uid in update:
                robot_repository.update(robot_model)
            if robot_model.uid in delete:
                robot_repository.delete(robot_model.uid)
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="save_robots",
            entity_type="Robot",
            exception=e
        )


@router.delete("/{robot_uid}")
async def delete_robot(
        robot_uid: str,
        user: dict = Depends(require_authentication("delete robot")),
        robot_repository: RobotRepository = Depends(get_service_by_type(RobotRepository))
):
    try:
        RouteHelper.delete_entity(robot_repository, robot_uid, "Robot")
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="delete_robot",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.get("/{robot_uid}/current_angles")
async def get_robot_current_angles(
        robot_uid: str,
        user: dict = Depends(require_authentication("get robot current angles")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        angles = robot_service.get_angles(robot_uid)
        return angles
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_robot_current_angles",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/{robot_uid}/{position_uid}/move_to_position")
async def move_to_position(
        robot_uid: str,
        position_uid: str,
        user: dict = Depends(require_authentication("move robot to position")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService)),
        robot_positions_repository: RobotPositionsRepository = Depends(get_service_by_type(RobotPositionsRepository))
):
    try:
        position = RouteHelper.get_entity_by_id(robot_positions_repository, position_uid, "RobotPosition")
        position_model = RobotPositionsModel(**position)
        robot_service.move_to_position(robot_uid, position_model.angles, position_model.speed)
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="move_to_position",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/{robot_uid}/home")
async def home_robot(
        robot_uid: str,
        user: dict = Depends(require_authentication("home robot")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        def home_lambda(): robot_service.home(robot_uid)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, home_lambda)

        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="home_robot",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/{robot_uid}/set_angle")
async def set_angle_on_robot_joint(
        robot_uid: str,
        joint_data: dict,
        user: dict = Depends(require_authentication("set angle on robot joint")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        robot_service.set_angle_on_joint(robot_uid, joint_data["joint_number"], joint_data["angle"],
                                         joint_data["speed"])
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="set_angle_on_joint",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.get("/{robot_uid}/positions")
async def get_robot_positions(
        robot_uid: str,
        user: dict = Depends(require_authentication("get robot positions")),
        robot_positions_repository: RobotPositionsRepository = Depends(get_service_by_type(RobotPositionsRepository))
):
    try:
        q = Query()
        res = robot_positions_repository.find_by_query(q.robot_uid == robot_uid)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_robot_positions",
            entity_type="RobotPosition",
            entity_id=robot_uid,
            exception=e
        )


@router.delete("/{position_uid}/delete_position")
async def delete_robot_position(
        position_uid: str,
        user: dict = Depends(require_authentication("delete robot position")),
        robot_positions_repository: RobotPositionsRepository = Depends(get_service_by_type(RobotPositionsRepository))
):
    try:
        RouteHelper.delete_entity(robot_positions_repository, position_uid, "RobotPosition")
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="delete_robot_position",
            entity_type="RobotPosition",
            entity_id=position_uid,
            exception=e
        )


@router.post("/{robot_uid}/save_position")
async def save_robot_position(
        robot_uid: str,
        position_data: dict,
        user: dict = Depends(require_authentication("save robot position")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService)),
        robot_positions_repository: RobotPositionsRepository = Depends(get_service_by_type(RobotPositionsRepository))
):
    try:
        current_angles = robot_service.get_angles(robot_uid)
        model = RobotPositionsModel(uid=position_data["uid"], angles=current_angles,
                                    components=position_data["components"],
                                    speed=position_data["speed"],
                                    robot_uid=robot_uid,
                                    name=position_data["name"])
        RouteHelper.create_entity(robot_positions_repository, model, "RobotPosition")
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="save_robot_position",
            entity_type="RobotPosition",
            entity_id=robot_uid,
            exception=e
        )


@router.put("/{robot_uid}/update_position")
async def update_robot_position(
        robot_uid: str,
        position_data: RobotPositionsModel,
        user: dict = Depends(require_authentication("update robot position")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService)),
        robot_positions_repository: RobotPositionsRepository = Depends(get_service_by_type(RobotPositionsRepository))
):
    try:
        angles = robot_service.get_angles(robot_uid)
        position_data.angles = angles
        RouteHelper.update_entity(robot_positions_repository, position_data, "RobotPosition")
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="update_robot_position",
            entity_type="RobotPosition",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/{robot_uid}/release_servos")
async def release_servos(
        robot_uid: str,
        user: dict = Depends(require_authentication("release robot servos")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        robot_service.release_servos(robot_uid)
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="release_servos",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )


@router.post("/{robot_uid}/power_servos")
async def power_on_servos(
        robot_uid: str,
        user: dict = Depends(require_authentication("power robot servos")),
        robot_service: RobotService = Depends(get_service_by_type(RobotService))
):
    try:
        robot_service.power_servos(robot_uid)
        return RouteHelper.create_success_response()
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="power_servos",
            entity_type="Robot",
            entity_id=robot_uid,
            exception=e
        )
