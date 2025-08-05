import serial.tools.list_ports

from src.metaclasses.singleton import Singleton


class PortManager(metaclass=Singleton):
    def __init__(self):
        self.vendors = ["Arduino Uno", "USB Serial Device", "USB-SERIAL CH340", "USB Serial Port", "MARLIN_STM32G0B1RE CDC in FS"]

    async def get_available_ports(self):
        ports = []
        for comport in serial.tools.list_ports.comports():
            par_ind = comport.description.rfind(" ")
            device_name = comport.description[:par_ind]
            if device_name in self.vendors:
                ports.append(comport.device)

        return ports

    @staticmethod
    async def get_available_ports_ultra_arm():
        ports = []
        for comport in serial.tools.list_ports.comports():
            if comport.pid == 29987 and comport.vid == 6790:
                ports.append(comport.device)

        return ports


# if __name__ == "__main__":
#     for comport in serial.tools.list_ports.comports():
#         par_ind = comport.description.rfind(" ")
#         device_name = comport.description[:par_ind]
