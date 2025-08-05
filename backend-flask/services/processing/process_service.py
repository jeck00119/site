import asyncio
import logging
import os
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Lock

import cv2
import numpy

# Set up logging for this module
logger = logging.getLogger(__name__)

from repo.repositories import ComponentsRepository, RobotPositionsRepository
from services.algorithms.algorithms_service import AlgorithmsService
from services.components.components_service import ComponentsService
from services.configurations.configurations_service import ConfigurationService
from services.dataman.dataman_service import DatamanService
from services.image_source.image_source_service import ImageSourceService
from services.inspection_list.inspection_list_service import InspectionListService
from services.itac.itac_service import ItacService
from services.processing.component_processing_thread import ComponentProcessingThread
from services.robot.robot_service import RobotService
from src.metaclasses.singleton import Singleton


class ProcessStates(Enum):
    IDLE = 1
    RUNNING = 2
    STOPPING = 3
    STOPPED = 4


@dataclass
class Task:
    frame: numpy.ndarray
    component_id: str


class ProcessService(metaclass=Singleton):
    def __init__(self):
        self.components_service = ComponentsService()
        self.algorithms_service = AlgorithmsService()
        self.components_repository = ComponentsRepository()
        self.interpreter_service = InspectionListService()
        self.itac_service = ItacService()
        self.configuration_service = ConfigurationService()
        self.robot_service = RobotService()
        self.robot_repository = RobotPositionsRepository()
        self.image_source_service = ImageSourceService()
        self.datamanService = DatamanService()

        self._process_state_info_deque: deque = deque(maxlen=100)

        self.capability_mode_state = False
        self.capability_mode_target = 0
        self.offset_mode_state = False
        self.itac_status = False
        self._process_state = ProcessStates.IDLE

        self.cable_algorithm = None
        self.image_source_uid = None

        self.state_lock = Lock()
        self.components_repo_lock = Lock()

        self.fail_retries = 3
        self.save_image_flag = False

        logger.info(f"Robot repository database: {self.robot_repository.db}")
        self.robot_positions = None
        self.task_queue = None
        self.component_processing_thread = None

    def set_save_image_flag(self, value):
        self.save_image_flag = value

    # event first dmc etc
    def add_process_status_to_ws_deque(self, status):
        self._process_state_info_deque.append(status)

    def read_process_status_to_ws_deque(self):
        if self._process_state_info_deque:
            return self._process_state_info_deque.popleft()
        else:
            return None

    async def start_process(self, offline=False):
        self.state_lock.acquire()
        self._process_state = ProcessStates.RUNNING
        self.state_lock.release()

        self.robot_positions = self.robot_repository.read_all()

        loop = asyncio.get_running_loop()
        if offline:
            await loop.run_in_executor(None, self._start_sm_offline)
        else:
            # self.itac_service.set_active(True)

            self.add_process_status_to_ws_deque(
                {'event': 'process_status', 'data': 'Initializing ITAC'})
            # self.itac_service.initialize()

            self.add_process_status_to_ws_deque(
                {'event': 'process_status', 'data': 'Initializing Cognex'})
            # self.datamanService.initialize()
            
            # Run blocking robot operations in executor to avoid blocking event loop
            await loop.run_in_executor(None, self._initialize_robot_and_start)
            
    def _initialize_robot_and_start(self):
        """Initialize robot and start processing - runs in thread executor"""
        try:
            top_robot = self.robot_service.get_robot_by_name("TopSideUltraArm")
            top_robot.home()
            top_robot.set_speed_mode(2)
            self.interpreter_service.load_inspection_list()
            self._start_sm()
        except Exception as e:
            logger.error(f"Error initializing robot and starting process: {e}")
            raise

    def stop_process(self):
        self.state_lock.acquire()
        self._process_state = ProcessStates.STOPPED
        self.state_lock.release()

    def hvh_process(self):
        self.task_queue = Queue()
        self.component_processing_thread = ComponentProcessingThread(process_queue=self.task_queue,
                                                                     components_repository=self.components_repository,
                                                                     algorithms_service=self.algorithms_service,
                                                                     interpreter_service=self.interpreter_service,
                                                                     components_repo_lock=self.components_repo_lock)

        self.component_processing_thread.set_running(True)
        self.component_processing_thread.start()

        top_robot = self.robot_service.get_robot_by_name("TopSideUltraArm")

        logger.info(f"Robot repository database: {self.robot_repository.db}")

        for position in self.robot_positions:
            logger.debug("Moving to next robot position")
            # Non-blocking robot movement and processing
            self._process_robot_position(position)
            
    def _process_robot_position(self, position):
        """Process a robot position with proper error handling"""
        try:
            self.robot_service.move_to_position(position["robot_uid"], position["angles"], position["speed"])
            time.sleep(2)  # This should ideally be replaced with a proper wait mechanism
            
            for component in position["components"]:
                self._process_component(component)
        except Exception as e:
            logger.error(f"Error processing robot position: {e}")
            
    def _process_component(self, component):
        """Process a single component with proper locking"""
        try:
            self.components_repo_lock.acquire()
            c = self.components_repository.read_id(component)
            self.components_repo_lock.release()
            
            logger.info(f"Loading camera settings for component: {c['name']}")
            self.image_source_service.load_settings_to_image_source(uid=c["image_source_uid"])
            time.sleep(1)  # Camera settling time
            
            frame = self.image_source_service.grab_from_image_source(uid=c["image_source_uid"])
            timestamp = ''.join(str(time.time()).split('.'))
            filename = timestamp + '_original.png'
            cv2.imwrite(filename, frame)
            
            task = Task(frame=frame, component_id=component)
            self.task_queue.put(task)
        except Exception as e:
            logger.error(f"Error processing component {component}: {e}")
        finally:
            # Ensure lock is always released
            if self.components_repo_lock.locked():
                self.components_repo_lock.release()

        self.component_processing_thread.set_running(False)
        top_robot.initial_position()
        self.component_processing_thread.join()

        res = self.interpreter_service.show_results()
        self.add_process_status_to_ws_deque({'event': 'done_results', 'data': res})

    def cable_inspection(self, cable_algorithm, image_source_uid):
        stopped = False
        inspections_tried = 0

        send_socket_data = True

        while True:
            result = self.algorithms_service.process_algorithm(cable_algorithm, image_source_uid)

            if send_socket_data:
                self.add_process_status_to_ws_deque(
                    {'event': 'process_status', 'data': 'Searching for cable components...'})
                send_socket_data = False

            heads = result.data["head_none_count"] + result.data["head_red_count"] + result.data["head_blue_count"] + \
                    result.data["head_black_count"]

            self.interpreter_service.add_inspection(result.data)
            self.interpreter_service.set_results_from_measurements()

            if heads != 0:
                if self.interpreter_service.has_fails():
                    inspections_tried += 1
                else:
                    break

            if inspections_tried == self.fail_retries:
                break

            self.state_lock.acquire()
            current_state = self._process_state
            self.state_lock.release()

            if current_state != ProcessStates.RUNNING:
                stopped = True
                break

        if not stopped:
            if self.interpreter_service.has_fails() and self.save_image_flag:
                timestamp = str(time.time()).split('.')[0]
                filename = timestamp + '.png'
                result_filename = timestamp + '_result.png'
                dirname = self.configuration_service.get_current_configuration_part_number()

                if not os.path.isdir(dirname):
                    os.makedirs(dirname)

                cv2.imwrite(f"{dirname}/{filename}", result.image)
                cv2.imwrite(f"{dirname}/{result_filename}", result.imageRoi)

            self.interpreter_service.add_image("CABLE", result.imageRoi)
            res = self.interpreter_service.show_results()
            self.add_process_status_to_ws_deque({'event': 'done_results', 'data': res})

    def ibs_process(self):
        self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Waiting for DMC'})
        # byte_res = self.itac_service.wait_for_data("IBS")

        self.datamanService.clear_data()
        self.datamanService.reset_serial_buffer()

        processed_dmc = self.wait_for_dmc()

        logger.info(f"DMC: {processed_dmc}")

        self.add_process_status_to_ws_deque({'event': 'dmc', 'data': processed_dmc})

        self.itac_service.send_serial_number("IBS", processed_dmc)

        byte_res = self.itac_service.wait_for_data("IBS")

        res = byte_res.decode()

        data_split = res.split(';')

        logger.info(f"Data split: {data_split}")

        response = data_split[1][0]
        part_number = data_split[2][:-2]

        logger.info(f"ITAC Response: {response}")
        logger.info(f"PART NUMBER: {part_number}")

        if not int(response):
            self.configuration_service.load_configuration_part_number(part_number)

            if self.configuration_service.get_configuration_flag_process():
                self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Loading Inspection List'})
                self.interpreter_service.load_inspection_list()

                if self.cable_algorithm is None:
                    self.add_process_status_to_ws_deque(
                        {'event': 'process_status', 'data': 'Initializing Algorithm'})

                    components = self.components_repository.read_all()
                    cable_component = components[0]

                    self.cable_algorithm = self.algorithms_service.create_algorithm(
                        cable_component['algorithm_uid'])
                    self.image_source_uid = cable_component['image_source_uid']
                    logger.info(f"Cable algorithm: {self.cable_algorithm}")

                self.configuration_service.reset_configuration_flag_process()

            self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Inspecting Cable'})
            self.cable_inspection(self.cable_algorithm, self.image_source_uid)

            self.itac_service.send_results("IBS", not self.interpreter_service.has_fails(), processed_dmc)
            byte_res = self.itac_service.wait_for_data("IBS")

            if byte_res and byte_res != '':
                res = byte_res.decode()
                data_split = res.split(';')

                response = data_split[1][0]

                if not int(response):
                    self.add_process_status_to_ws_deque({'event': 'ITAC Status', 'data': 'Received ACK from ITAC'})
                else:
                    self.add_process_status_to_ws_deque({'event': 'ITAC Status', 'data': 'Received NACK from ITAC'})
        else:
            self.add_process_status_to_ws_deque(
                {'event': 'ITAC Status', 'data': 'Inspection was aborted by ITAC (NACK)'})

    def ibs_process_offline(self):
        if self.configuration_service.get_configuration_flag_process():
            self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Loading Inspection List'})
            self.interpreter_service.load_inspection_list()

            if self.cable_algorithm is None:
                self.add_process_status_to_ws_deque(
                    {'event': 'process_status', 'data': 'Initializing Algorithm'})

                components = self.components_repository.read_all()
                if not components:
                    print("No components configured - cannot initialize cable algorithm")
                    return
                cable_component = components[0]

                self.cable_algorithm = self.algorithms_service.create_algorithm(
                    cable_component['algorithm_uid'])
                self.image_source_uid = cable_component['image_source_uid']

            self.configuration_service.reset_configuration_flag_process()

        if self.cable_algorithm is not None and self.image_source_uid is not None:
            self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Inspecting Cable'})
            self.cable_inspection(self.cable_algorithm, self.image_source_uid)
        else:
            self.add_process_status_to_ws_deque({'event': 'process_status', 'data': 'Cannot start inspection - no components or image source configured'})
            print("Cannot start cable inspection - cable_algorithm or image_source_uid is None")

    def _start_sm(self):
        while True:
            self.state_lock.acquire()
            current_state = self._process_state
            self.state_lock.release()

            if current_state != ProcessStates.RUNNING:
                break

            self.hvh_process()

            # time.sleep(0.4)

        # self.itac_service.set_active(False)
        # self.itac_service.un_initialize()

    def _start_sm_offline(self):
        while True:
            self.state_lock.acquire()
            current_state = self._process_state
            self.state_lock.release()

            if current_state != ProcessStates.RUNNING:
                break

            self.ibs_process_offline()

    @staticmethod
    def read_dmc_data(filename):
        serial_number = ''
        part_number = ''

        with open(filename) as dmc_file:
            lines = dmc_file.readlines()

            if len(lines) != 0:
                serial_number, part_number = lines[0].split(';')

        return serial_number, part_number

    def wait_for_dmc(self):
        while True:
            data = self.datamanService.get_dmc_data()

            if data != '':
                break

        return data
