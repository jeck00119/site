import json
import socket
import struct
import subprocess
import threading
import time
import logging


AUTO_START_GOCATOR_SERVER = False


# Decorator for methods that require feedback in the GocatorClient class
# Timeout is hardcoded to 5 seconds
def require_ack(method):
    def ack_method(*args, **kwargs):
        # first argument is always the object
        ref = args[0]

        if 'ack' in kwargs:
            ack = kwargs['ack']
        else:
            # treat missing ack as false
            ack = False

        if ack:
            ref.feedback = False
        else:
            ref.feedback = True

        method(*args, **kwargs)

        counter = 0

        while not ref.feedback and counter < 500:
            time.sleep(0.01)
            counter += 1
    return ack_method


class ProcessingThread(threading.Thread):
    def __init__(self, top, step_size, config_path, parent=None):
        super(ProcessingThread, self).__init__()
        self.cntrl = parent
        self.top = top
        self.stepSize = step_size
        self.configPath = config_path

    def generate_mesh_points(self, width, length, z):
        pos = []
        width = int(width / (self.stepSize + 1))
        length = int(length / (self.stepSize + 1))

        x_coord = 0
        y_coord = 0

        for i in range(len(z)):
            if i % width != width - 1:
                if z[i] != -32768:
                    pos.append([x_coord / 10000, y_coord / 10000, z[i] / 10000])
                x_coord += 10 * (self.stepSize + 1)
            else:
                if z[i] != -32768:
                    pos.append([x_coord / 10000, y_coord / 10000, z[i] / 10000])
                x_coord = 1
                y_coord += 40

        pos = np.array(pos, dtype=float)
        minZ = np.min(pos[:, 2])
        pos[:, 2] -= minZ

        return np.array(pos)

    def read_points(self, file_path):
        with np.load(file_path) as gocator_data:
            data = gocator_data["z"]

        return data[0], data[1], data[2:]

    def run(self) -> None:
        if self.top:
            width, length, z = self.read_points(self.configPath + "\\GocatorTopData3D.npz")
            if width != 0 and length != 0:
                mesh = self.generate_mesh_points(width, length, z)
                self.cntrl.set_top_mesh(mesh)
                self.cntrl.meshTopSignal.emit(mesh)
        else:
            width, length, z = self.read_points(self.configPath + "\\GocatorBottomData3D.npz")
            if width != 0:
                mesh = self.generate_mesh_points(width, length, z)
                self.cntrl.set_bottom_mesh(mesh)
                self.cntrl.meshBottomSignal.emit(mesh)


class GocatorClient(object):
    def __init__(self, serial_numbers, config_path, server_file_path, server_ip_address="127.0.0.1", port=1111,
                 step_size=2):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.serverIpAddress = server_ip_address
        self.serialNumbers = serial_numbers
        self.serverFilePath = server_file_path

        self.meshPosTop = []
        self.meshPosBottom = []
        self.measurementsTop = None
        self.measurementsBottom = None
        self.alignmentStatusTop = True
        self.alignmentStatusBottom = True

        self.stepSize = step_size
        self.configPath = config_path

        self.port = port
        self.s = None

        self.topResourceLock = threading.Lock()
        self.bottomResourceLock = threading.Lock()

        self.serverThread = None
        self.clientThread = None
        self.listenerThread = None
        self.running = False
        self.lastMessageTime = None
        self.processingThread = None

        # Improvizatie Stefan
        self.meastpReceived = False
        self.measbmReceived = False

        self.feedback = False

        self.botLaserID = None
        self.topLaserID = None

        # bottom laser is removed from the system
        #self.register_laser(self.botLaserID)

    def get_id(self):
        return self.botLaserID

    def start_server(self):
        if AUTO_START_GOCATOR_SERVER:
            subprocess.run([self.serverFilePath])

    def start(self):
        self.serverThread = threading.Thread(target=self.start_server)
        self.serverThread.name = "Gocator client thread"
        self.serverThread.start()

        time.sleep(3)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.serverIpAddress, self.port))

            self.load_configuration_settings(False)

            self.lastMessageTime = time.time()

            self.running = True

            self.botLaserID = self.serialNumbers
            # !!! it's not working - change logic for multiple gocators (start server only once)
            #self.botLaserID = self.serialNumbers[0]
            #self.topLaserID = self.serialNumbers[1]
            self.register_laser(self.botLaserID)

            self.clientThread = threading.Thread(target=self.listen_for_data)
            self.clientThread.name = "Gocator data listening thread"
            self.clientThread.start()
        except: #ConnectionRefusedError as ex:
            self.logger.error("Gocator service connection timeout error.")

    def release_resources(self):
        self.close_server()

        try:
            self.serverThread.join()
            self.running = False
            self.clientThread.join()
        except Exception as e:
            self.logger.error(e)
        try:
            self.s.close()
        except Exception as e:
            self.logger.error(e)

    def _send(self, command, ack: bool = False):
        data = bytes(command, 'utf-8')
        ack_bytes = struct.pack("?", ack)

        size = len(data)
        size_bytes = struct.pack("i", size)
        self.s.sendall(size_bytes + ack_bytes + data)

    def load_configuration_settings(self, ack: bool = False):
        command = f"loadcf{self.configPath};{str(self.stepSize)};{self.serialNumbers[0]};{self.serialNumbers[1]}"
        self._send(command, ack)

    def close_server(self):
        self._send("close;0", False)

    def register_laser(self, laserID):
        self._send("register;" + laserID)

    def wait_for_feedback(self):
        counter = 0
        while not self.feedback and counter < 500:
            time.sleep(0.01)
            counter += 1

    @require_ack
    def load_job_top(self, job_name: str, ack: bool = False):
        self._send("load;" + self.topLaserID + ';' + job_name, ack)

    @require_ack
    def load_job_bottom(self, job_name: str, ack: bool = False):
        self._send("load;" + self.botLaserID + ';' + job_name, ack)

    @require_ack
    def start_sensor_top(self, ack: bool = False):
        self._send("start;" + self.topLaserID, ack)

    @require_ack
    def start_sensor_bottom(self, ack: bool = False):
        self._send("start;" + self.topLaserID, ack)

    @require_ack
    def stop_sensor_top(self, ack: bool = False):
        self._send("stop;" + self.topLaserID, ack)

    @require_ack
    def stop_sensor_bottom(self, ack: bool = False):
        self._send("stop;" + self.botLaserID, ack)

    @require_ack
    def stop_both_sensors(self, ack: bool = False):
        self._send("stopall;0", ack)

    @require_ack
    def start_both_sensors(self, ack: bool = False):
        self._send("startall;0", ack)

    # def load_job_both(self, job_name_bottom: str, job_name_top: str, ack: bool):
    #     command = f"loadbh{job_name_bottom};{str(job_name_top)}"
    #     self._send(command, ack)

    def get_server_data(self):
        try:
            msg_size = self.s.recv(4, socket.MSG_WAITALL)

            unpacked_msg_size = struct.unpack('i', msg_size)[0]
        except:
            return None
        data = b''
        while len(data) < unpacked_msg_size:
            if unpacked_msg_size - len(data) > 4096:
                try:
                    data += self.s.recv(4096)
                except ConnectionResetError:
                    return None
            else:
                try:
                    data += self.s.recv(unpacked_msg_size - len(data))
                except ConnectionResetError:
                    return None

        received_data = data[:unpacked_msg_size]
        return received_data

    def wait_data_receive_top(self, timeout=5):
        start = time.time()
        while not self.meastpReceived:
            stop = time.time()
            if (stop - start) > timeout:
                break
            time.sleep(0.01)

        self.meastpReceived = False

    def wait_data_receive_bottom(self, timeout=5):
        start = time.time()
        while not self.measbmReceived:
            stop = time.time()
            if (stop - start) > timeout:
                break
            time.sleep(0.01)

        self.measbmReceived = False

    def listen_for_data(self):
        while self.running:
            received_data = self.get_server_data()

            if received_data is not None:
                msg = received_data.decode("utf-8")
                split = msg.split(';', 2)

                command = split[0]
                id = int(split[1])
                if len(split) > 2:
                    payload = split[2]

                if command == "meas":
                    data = json.loads(payload)
                    if id == self.topLaserID:
                        self.set_top_measurements(data)
                        self.meastpReceived = True
                    else:
                        self.set_bottom_measurements(data)
                        self.measbmReceived = True
                elif command == "feedback":
                    self.feedback = True
                elif command == "meshtp":
                    self.logger.debug("meshtp")
                    # self.processingThread = ProcessingThread(top=True, step_size=self.stepSize, config_path=self.configPath, parent=self)
                    # self.processingThread.start()
                elif command == "meshbm":
                    self.logger.debug("meshbm")
                    # self.processingThread = ProcessingThread(top=False, step_size=self.stepSize, config_path=self.configPath, parent=self)
                    # self.processingThread.start()
                elif command == "algntp":
                    data = json.loads(payload)
                    self.alignmentStatusTop = True if data == "True" else False

                elif command == "algnbm":
                    data = json.loads(payload)
                    self.alignmentStatusBottom = True if data == "True" else False

                elif command == "feedtp" or command == "feedbm":
                    feedback_code = struct.unpack('?', payload.encode('utf-8'))[0]
                    if self.waitForFeedback:
                        self.feedback = True
                        self.waitForFeedback = False
                elif command == "infobm":
                    data = json.loads(payload)
                elif command == "infotp":
                    data = json.loads(payload)

            time.sleep(0.5)

    def reset_connection(self):
        try:
            self.serverThread.join()
            self.running = False
            self.clientThread.join()
        except Exception as e:
            self.logger.error(e)
        try:
            self.s.close()
        except Exception as e:
            self.logger.error(e)

        self.start()

    def get_top_mesh(self):
        self.topResourceLock.acquire()
        mesh = self.meshPosTop
        self.meshPosTop = None
        self.topResourceLock.release()
        return mesh

    def set_top_mesh(self, mesh):
        self.topResourceLock.acquire()
        self.meshPosTop = mesh
        self.topResourceLock.release()

    def get_top_measurements(self):
        self.topResourceLock.acquire()
        measurements = self.measurementsTop
        self.logger.debug(f"Received Top measurements {measurements}")
        self.measurementsTop = None
        self.topResourceLock.release()
        return measurements

    def set_top_measurements(self, measurements):
        self.topResourceLock.acquire()
        self.measurementsTop = measurements
        self.logger.debug(f"measurements top are {measurements}")
        self.topResourceLock.release()

    def get_bottom_mesh(self):
        self.bottomResourceLock.acquire()
        mesh = self.meshPosBottom
        self.meshPosBottom = None
        self.bottomResourceLock.release()
        return mesh

    def set_bottom_mesh(self, mesh):
        self.bottomResourceLock.acquire()
        self.meshPosBottom = mesh
        self.bottomResourceLock.release()

    def get_bottom_measurements(self):
        self.bottomResourceLock.acquire()
        measurements = self.measurementsBottom
        self.logger.debug(f"Received Bottom measurements {measurements}")
        self.measurementsBottom = None
        self.bottomResourceLock.release()
        return measurements

    def set_bottom_measurements(self, measurements):
        self.bottomResourceLock.acquire()
        self.measurementsBottom = measurements
        self.logger.debug(f"measurements bot are {measurements}")
        self.bottomResourceLock.release()


class GocatorClientDummy(object):
    def __init__(self, serial_numbers=1, config_path=1, server_file_path=1, server_ip_address="127.0.0.1", port=1111,
                 step_size=2):
        super().__init__()
        self.serverIpAddress = server_ip_address
        self.serialNumbers = serial_numbers
        self.serverFilePath = server_file_path

        self.meshPosTop = []
        self.meshPosBottom = []
        self.measurementsTop = None
        self.measurementsBottom = None

        self.stepSize = step_size
        self.configPath = config_path

        self.port = port
        self.s = None

        self.topResourceLock = threading.Lock()
        self.bottomResourceLock = threading.Lock()

        self.serverThread = None
        self.listenerThread = None
        self.running = False
        self.lastMessageTime = None

    def start_server(self):
        pass

    def start(self):
        self.logger.debug("Dummy Gocator client started.")

    def check_connection(self):
        pass

    def release_resources(self):
        pass

    def load_configuration_settings(self):
        pass

    def close_server(self):
        pass

    def load_job_top(self, job_name: str):
        pass

    def load_job_bottom(self, job_name: str):
        pass

    def start_sensor_top(self):
        pass

    def start_sensor_bottom(self):
        pass

    def stop_sensor_top(self):
        pass

    def stop_sensor_bottom(self):
        pass

    def connect_to_s(self):
        pass

    def disconnect_from_s(self):
        pass

    def connect_top(self):
        pass

    def connect_bottom(self):
        pass

    def disconnect_top(self):
        pass

    def disconnect_bottom(self):
        pass

    def get_server_data(self):
        pass

    def generate_mesh_points(self, width, length, z):
        pass

    def read_points(self, file_path):
        pass

    def listen_for_data(self):
        pass

    def get_top_mesh(self):
        pass

    def set_top_mesh(self, mesh):
        pass

    def get_top_measurements(self):
        pass

    def set_top_measurements(self, measurements):
        pass

    def get_bottom_mesh(self):
        pass

    def set_bottom_mesh(self, mesh):
        pass

    def get_bottom_measurements(self):
        pass

    def set_bottom_measurements(self, measurements):
        pass
