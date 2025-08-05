import importlib
import os
import pathlib
import pickle
import time
import traceback
import logging

try:
    from xarm.tools import utils
except:
    pass
try:
    from xarm.wrapper import XArmAPI
except:
    pass

SIMULATE_BOARD_INSIDE_SYSTEM = True


class xArmRobotCallBack():
    position = 0
    callback = None
    sleep = None


class XArmRobot(object):
    def __init__(self, ip_robot):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.arm = None
        self.ipRobot = ip_robot
        self.last_movement = 0

        self.params = {'speed': 100, 'acc': 2000, 'angle_speed': 20, 'angle_acc': 500, 'events': {}, 'variables': {},
                       'callback_in_thread': True, 'quit': False}

        self.last_trajectory = None

        self.moved = False

        self.hash_file_name = "lastpos"
        self.hash_file_name_real = self.hash_file_name + ".real"

        self._hash_table = self.getHashList()

        for key, val in self._hash_table.items():
            self.logger.debug(f"{key} : {val}")
        #self.init_gpio()

    def get_connection_id(self):
        return self.ipRobot

    def init_gpio(self):

        gpio_list = [{'gpio': 0, 'value': 0},
                     {'gpio': 1, 'value': 0},
                     {'gpio': 2, 'value': 0},
                     {'gpio': 3, 'value': 0},
                     {'gpio': 4, 'value': 0},
                     {'gpio': 5, 'value': 0},
                     {'gpio': 6, 'value': 0},
                     {'gpio': 7, 'value': 0}]

        for gpio in gpio_list:
            self.SetGpio(gpio['gpio'], gpio['value'])

    def initialize(self):
        try:
            self.arm = XArmAPI(self.ipRobot)
            self.clean_warning()

            self.set_callback()
        except Exception:
            pass

    def un_initialize(self):
        self.release_callback()

    def EMRR_STOP(self):
        self.arm.emergency_stop()

    def safe_move_init_aruco_2(self):
        pass

    def safe_move_init_aruco_1(self):
        pass

    def safe_move_init(self):
        self.moved = False
        self.last_trajectory = None
        self.last_movement = 0
        self.clean_warning()

        with open(self.hash_file_name_real, 'r') as f:
            hash = f.read()

        # Return false if last used trajectory is not a valid one
        if hash not in self._hash_table:
            return False

        pos = self.getPosition()
        res = []

        for trajectory in self._hash_table[hash]:
            pos_t = trajectory['angle']
            res.append(self.get_pos_diff(pos, pos_t))

        min_index = res.index(min(res))

        for index, trajectory in enumerate(self._hash_table[hash]):
            if index < min_index:
                continue

            if trajectory.get("angle_speed") is not None:
                if not (index > 0 and self._hash_table[hash][index - 1].get("angle_speed")) == trajectory.get(
                        "angle_speed"):
                    self.params['angle_speed'] = trajectory.get("angle_speed")

            if trajectory.get("angle_acc") is not None:
                if not (index > 0 and self._hash_table[hash][index - 1].get("angle_acc")) == trajectory.get("angle_acc"):
                    self.params['angle_acc'] = trajectory.get("angle_acc")

            if self.arm.error_code == 0 and not self.params['quit']:
                code = self.arm.set_servo_angle(angle=trajectory.get("angle"), speed=self.params['angle_speed'],
                                                mvacc=self.params['angle_acc'], wait=False,
                                                radius=trajectory.get("radius"))
                if code != 0:
                    self.params['quit'] = True
                    self.pprint('set_servo_angle, code={}'.format(code))

        return True

    def get_pos_diff(self, pos1, pos2):

        diff = 0
        for val1, val2 in zip(pos1, pos2):
            diff += abs(val1 - val2)

        return diff

    def get_temp(self):
        temps = self.arm.temperatures if self.arm is not None else [0]*5
        return temps

    def get_status(self):
        return self.arm.get_state()

    def clean_warning(self):
        if self.arm:
            self.arm.clean_warn()
            self.arm.clean_error()
            self.arm.motion_enable(True)
            self.arm.set_mode(0)
            self.arm.set_state(0)
            time.sleep(1)

    def pprint(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    # Register error/warn changed callback
    def error_warn_change_callback(self, data):
        if data and data['error_code'] != 0:
            self.params['quit'] = True
            self.logger.debug("err={}, quit".format(data["error_code"]))
            self.arm.release_error_warn_changed_callback(self.error_warn_change_callback)

    # Register state changed callback
    def state_changed_callback(self, data):
        if data and data['state'] == 4:
            if self.arm.version_number[0] >= 1 and self.arm.version_number[1] >= 1 and self.arm.version_number[2] > 0:
                self.params['quit'] = True
                self.logger.debug("state=4, quit")
                self.arm.release_state_changed_callback(self.state_changed_callback)

    # Register counter value changed callback
    def count_changed_callback(self, data):
        if not self.params['quit']:
            self.logger.debug("counter val: {}".format(data["count"]))

    # Register connect changed callback
    def connect_changed_callback(self, data):
        if data and not data['connected']:
            self.params['quit'] = True
            self.logger.debug("disconnect, connected={}, reported={}, quit".format(data["connected"], data["reported"]))
            self.arm.release_connect_changed_callback(self.error_warn_change_callback)

    def set_callback(self):
        if self.arm:
            self.arm.register_error_warn_changed_callback(self.error_warn_change_callback)
            self.arm.register_state_changed_callback(self.state_changed_callback)
            if hasattr(self.arm, 'register_count_changed_callback'):
                self.arm.register_count_changed_callback(self.count_changed_callback)
            self.arm.register_connect_changed_callback(self.connect_changed_callback)

    def release_callback(self):
        if self.arm:
            self.arm.release_error_warn_changed_callback(self.state_changed_callback)
            self.arm.release_state_changed_callback(self.state_changed_callback)
            if hasattr(self.arm, 'release_count_changed_callback'):
                self.arm.release_count_changed_callback(self.count_changed_callback)
            self.arm.release_connect_changed_callback(self.error_warn_change_callback)

    def run_trajectory_test(self, xArm_dictionaryList, nr_pos=None, callback=None):
        self.saveHash(xArm_dictionaryList)

        self.safe_move_init()

    def run_trajectory(self, xArm_dictionaryList, run_from=None, run_to=None, callback:xArmRobotCallBack=None, ignoreHash=False):
        # Callback[0][0] = position to execute the callback
        # Callback[0][1] = callback name
        # Callback[0][2] = None -> wait = True or False (the value is taken from the script)
        # Callback[0][2] = sleep value (sleep(0.5), sleep(1), etc)
        #
        # Callback = [4,None,None]         = wait for the robot to arrive at position 4, then finish the traj
        # Callback = [4,callbak_name,None] = wait for the robot to arrive at position 4, execute the callback, then
        #                                    finish the traj
        # Callback = [4,None, 0.5]         = loop through each traj step, until step 4 (without wait). When the loop
        #                                    reaches index 4, sleep 0.5 s and then finish the traj and continue the flow
        # Callback = [4,callback_name, 0.5]= loop through each traj step, until step 4 (without wait). When the loop
        #                                    reaches index 4, sleep 0.5 s and then execute the callback.
        #                                    (Using last 2 methods you will get a smoother effect)
        #

        if callback is not None:
            callback.sort(key=lambda x: x.position)

        codeServo = 0
        codeVacuum = 0

        if (self.moved and xArm_dictionaryList == self.last_trajectory) or not self.moved:
            if not ignoreHash:
                self.saveHash(xArm_dictionaryList)

            for index, trajectory in enumerate(xArm_dictionaryList):
                if run_from is None:
                    if index < self.last_movement:
                        continue
                else:
                    if index < run_from:
                        continue

                if callback is not None and index == callback[0].position and callback[0].sleep is None:
                    wait = True
                    self.logger.debug("force wait")
                else:
                    wait = trajectory.get("wait")

                if trajectory.get("angle_speed") is not None:
                    if not (index > 0 and xArm_dictionaryList[index - 1].get("angle_speed")) == trajectory.get(
                            "angle_speed"):
                        self.params['angle_speed'] = trajectory.get("angle_speed")

                if trajectory.get("angle_acc") is not None:
                    if not (index > 0 and xArm_dictionaryList[index - 1].get("angle_acc")) == trajectory.get("angle_acc"):
                        self.params['angle_acc'] = trajectory.get("angle_acc")

                if self.arm.error_code == 0 and not self.params['quit']:
                    codeServo = self.arm.set_servo_angle(angle=trajectory.get("angle"), speed=self.params['angle_speed'],
                                                         mvacc=self.params['angle_acc'], wait=wait,
                                                         radius=trajectory.get("radius"))
                    if codeServo != 0:
                        self.params['quit'] = True
                        self.logger.debug("set_servo_angle, code={}".format(codeServo))

                if not SIMULATE_BOARD_INSIDE_SYSTEM:
                    if trajectory.get("vacuum") is not None:
                        if self.arm.error_code == 0 and not self.params['quit']:
                            codeVacuum = self.arm.set_suction_cup(trajectory.get("vacuum"), wait=True, delay_sec=0)
                            if codeVacuum != 0:
                                self.params['quit'] = True
                                self.logger.debug("set_suction_cup, code={}".format(codeVacuum))

                if self.params['quit'] or index == run_to:
                    break

                if callback is not None and index == callback[0].position:
                    if callback[0].sleep is not None:
                        self.logger.debug("sleeping")
                        time.sleep(callback[0].sleep)

                    if callback[0].callback is not None:
                        self.logger.debug(index)
                        callback[0].callback()

                    callback.pop(0)

                    if len(callback) == 0:
                        callback = None

        else:
            return False, codeServo, codeVacuum

        if run_to is not None:
            self.last_movement = run_to
            self.moved = True
            self.last_trajectory = xArm_dictionaryList
        else:
            self.last_movement = 0
            self.moved = False
            self.last_trajectory = None

        # return self.params['quit'], code
        return True, codeServo, codeVacuum

    def call1(self):
        self.logger.debug("it's working1")

    def call2(self):
        self.logger.debug("it's working2")

    def call3(self):
        self.logger.debug("it\'s working3")
    def getPosition(self):

        _, pos = self.arm.get_servo_angle()

        return pos

        # return [265.0, 42.0, -130.0, 85.0, 81.0]

    def saveHash(self, xArmDictionary):
        input = pickle.dumps(xArmDictionary)
        md5Hash = hashlib.md5(input)
        hash = md5Hash.hexdigest()

        with open(self.hash_file_name, 'w') as f:
            f.write(hash)
            f.close()

        os.replace(self.hash_file_name, self.hash_file_name_real)

    def getHashList(self):
        hash_table = {}

        try:
            path_of_the_directory = os.path.join(pathlib.Path(__file__).parent.resolve(), 'Dictionaries\\BMS_Farasis')
            dict_name = 'xArm_dictionary'

            for files in os.listdir(path_of_the_directory):
                if files.endswith('.py'):
                    full_path = os.path.join(path_of_the_directory, files)
                    spec = importlib.util.spec_from_file_location(dict_name, full_path)
                    xArmRobotDictionaty = spec.loader.load_module()

                    input = pickle.dumps(xArmRobotDictionaty.xArm_dictionary)
                    md5Hash = hashlib.md5(input)

                    hash_table[md5Hash.hexdigest()] = xArmRobotDictionaty.xArm_dictionary
        except WindowsError:
            pass

        return hash_table

    def SetGpio(self, gpio, value): # Door GPIO = 5
        if self.arm.error_code == 0 and not self.params['quit']:
            code = self.arm.set_cgpio_digital(gpio, value, delay_sec=0)
            if code != 0:
                self.params['quit'] = True
                self.logger.debug("set_cgpio_digital, code={}".format(code))


class XArmRobotDummy(object):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.arm = 1
        self.variables = {}
        self.last_movement = 0
        self.params = {'speed': 100, 'acc': 2000, 'angle_speed': 20, 'angle_acc': 500, 'events': {},
                       'variables': self.variables, 'callback_in_thread': True, 'quit': False}
        self.clean_warning()

        self.last_trajectory = None

        self.moved = False

    def safe_move_init(self):
        return True

    def un_initialize(self):
        pass

    def initialize(self):
        self.logger.debug("Dummy Robot initialized.")

    def get_init_objects_counter(self):
        return 1

    def get_temp(self):
        pass

    def clean_warning(self):
        pass
        time.sleep(1)

    def create_dictionary(self):
        pass

    def pprint(*args, **kwargs):
        pass

    # Register error/warn changed callback
    def error_warn_change_callback(self, data):
        pass

    # Register state changed callback
    def state_changed_callback(self, data):
        pass

    # Register counter value changed callback
    def count_changed_callback(self, data):
        pass

    # Register connect changed callback
    def connect_changed_callback(self, data):
        pass

    def set_callback(self):
        pass

    def release_callback(self):
        pass

    def run_trajectory(self, xArm_dictionaryList, run_from=None, run_to=None, callback=None, ignoreHash=False):
        return True, 0, 0


if __name__ == '__main__':
    robot = XArmRobot(ip_robot='192.168.1.237')
    robot.initialize()

