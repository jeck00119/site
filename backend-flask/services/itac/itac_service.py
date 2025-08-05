"""
Handles the Itac Workers and the connection the ITAC.
"""
import socket
import time
from threading import Thread

from repo.repositories import ItacRepository
from services.itac.itac_model import ItacModel
from src.metaclasses.singleton import Singleton


class ItacService(metaclass=Singleton):
    """
    Handles the workers.
    """
    itac_flag = False

    def __init__(self):
        super().__init__()
        self.itac_repository = ItacRepository()

        self.itac_workers: dict = {}
        self.trigger_itac = None
        self.trigger_callback = None

    def set_trigger_callback(self, callback):
        self.trigger_callback = callback

    def set_active(self, flag: bool):
        """Sets global ITAC status"""
        self.itac_flag = flag

    def get_worker(self, name=None):
        """Return workers after name"""
        for item in self.itac_workers.items():
            if item[0].startswith(name):
                return item[1]

        return False

    def _refresh_workers(self):
        """Refreshes the current workers from the db"""
        self.itac_workers.clear()
        repo_query = self.itac_repository.read_all()
        for itac in repo_query:
            itac_model = ItacModel(**itac)
            self.itac_workers[itac_model.name] = ItacWorker(itac_model)

    def initialize_trigger_itac(self):
        if self.itac_flag:
            itac = ItacModel(name="InspectionTrigger", destination_ip="10.169.215.67", destination_port=5000,
                             start_booking_code="", pass_booking_code="", fail_booking_code="", uid="")
            self.trigger_itac = ItacWorker(itac)
            self.trigger_itac.initialize()
            self.trigger_itac.listen(self.trigger_callback)

    def get_trigger_itac(self):
        return self.trigger_itac

    def initialize(self, name=None):
        """Initialize all the workers"""
        if self.itac_flag:
            self._refresh_workers()
            if name:
                self.itac_workers[name].initialize()
            else:
                for worker in self.itac_workers.values():
                    worker.initialize()
        else:
            pass

    def un_initialize(self, name=None):
        """Uninitialized all the workers"""
        if self.itac_flag:
            if name:
                self.itac_workers[name].un_initialize()
            else:
                for worker in self.itac_workers.values():
                    worker.un_initialize()
        else:
            pass

    def wait_for_data(self, name):
        try:
            return self.itac_workers[name].listen()
        except KeyError:
            return None

    def send_results(self, name, status, serial_number):
        self.itac_workers[name].send_results(status, serial_number)

    def send_serial_number(self, name, serial_number):
        self.itac_workers[name].send_serial_number(serial_number)

    def un_initialize_trigger_itac(self):
        if self.trigger_itac:
            self.trigger_itac.un_initialize()

    def get_init_objects_counter(self):
        """Used in circular loading."""
        return len(self.itac_workers)


class ItacWorker(Thread):
    """
    Itac worker. A class that handles created sockets.
    """

    def __init__(self, itac):
        super().__init__()
        self._itac: ItacModel = itac
        self._socket_itac = None

        self._async_status = 0
        self._running = False
        self._status = {}

    def _run_on_thread(func):
        """ Decorator to make methods async"""

        def wrapper(self, *args, **kwargs):
            thread = Thread(target=func, args=(self, *args), kwargs=kwargs)
            self._start_async()
            thread.start()

        return wrapper

    def check_itac_status(self, timeout=1):
        """ Returns itac status. Blocking until running is off or timeout"""
        timeout_start = time.time()
        while self._running and time.time() < timeout_start + timeout:
            time.sleep(0.1)

        if self._async_status == 0:
            return True, self._status.items()
        else:
            return False, self._status.items()

    def _start_async(self):
        self._async_status += 1
        self._running = True

    def _done_async(self, return_code, message_text):
        self._async_status -= 1
        self._running = False
        self._status = {return_code: message_text}

    @_run_on_thread
    def product_change(self, part_number: str, event_id):
        """
        The part number will be sent to the MES.Can be done at recipe load from HMI or when doing a home position.
        <STX>productChange;EventID;PartNumber<CR><LF>
        EventID - unique designator for telegrams.Can be defined by supplier. (example: "1" or "0001")
        PartNumber = defined field in HMI Recipe
        """
        data_telegram = f'\x02productChange;{event_id};{part_number}\r\n'
        self._send_telegram(data_telegram)

    @_run_on_thread
    def product_start(self, serial_number: str, event_id):
        """
        The part number will be sent to the MES.Can be done at recipe load from HMI or when doing a home position.
        EventID - unique designator for telegrams.Can be defined by supplier. (example: "1" or "0001")
        PartNumber = defined field in HMI Recipe
        <STX>productChange;EventID;PartNumber<CR><LF>
        """
        data_telegram = f'\x02productStart;{event_id};{serial_number}\r\n'
        self._send_telegram(data_telegram)

    @_run_on_thread
    def upload_data(self, serial_number: str, part_number: str, serial_number_state: str, measurements: list, event_id):
        """
        Process result to be sent to ITAC with measurements.
        Separate documentation will be provided for how and when the _str_states need to be sent.
        '<STX>uploadData;EventID;PartNumber;serialNumber;serialNumberState;NrOfMeasurements;[measurementData]<CR><LF>'
        """
        data_telegram = f'\x02uploadData;{event_id};{part_number};{serial_number};{serial_number_state};{measurements}\r\n'
        self._send_telegram(data_telegram)

    @_run_on_thread
    def update_macon(self, condition_code: str, event_id):
        """
        Separate documentation will be provided for how and when the _str_states need to be sent.
        <STX>updateMacon;EventID;conditionCode<CR><LF>
        """
        data_telegram = f'\x02updateMacon;{condition_code};{event_id}\r\n'
        self._send_telegram(data_telegram)

    @_run_on_thread
    def un_initialize(self):
        """Uninitialize individual worker. """
        try:
            self._socket_itac.close()
        except Exception as e:
            raise e

    def initialize(self):
        """Initialize individual worker."""
        self._socket_itac = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket_itac.settimeout(10)
        try:
            self._socket_itac.connect((self._itac.destination_ip, int(self._itac.destination_port)))
        except Exception as e:
            raise e

    def _send_telegram(self, telegram):
        try:
            self._socket_itac.send(bytearray(telegram, "utf-8"))
        except Exception as e:
            raise e
        # data_return = self._socket_itac.recv()
        #
        # return_code, message_text = str(data_return)
        # self._done_async(return_code, message_text)

    def listen(self):
        data_bytes = b''
        while data_bytes == b'':
            data_bytes = self._socket_itac.recv(256)
        print(f"Data bytes: {data_bytes}")
        return data_bytes

    def send_results(self, status, serial_number):
        if status:
            data_telegram = f'\x022100;{serial_number};{0}\r\n'
        else:
            data_telegram = f'\x022100;{serial_number};{1}\r\n'

        self._send_telegram(data_telegram)

    def send_serial_number(self, serial_number):
        data_telegram = f'\x021020;{serial_number}\r\n'
        self._send_telegram(data_telegram)


if __name__ == "__main__":
    worker = ItacWorker(ItacModel())
    worker.update_macon('1', '1')
    print('DOne Async Call')
    time.sleep(1)
    print(worker.check_itac_status(2))
    print('DOne main')
