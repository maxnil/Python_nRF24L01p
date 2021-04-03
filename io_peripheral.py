import sys


global_spidriver = None


class SPI:
    """Common SPI class for Raspberry Pi RP2040 MCU, SPIDriver USB dongle (Mac/PC) and Raspberry Pi computer"""
    def __init__(self, spi_id=0, baud_rate=1000000, spi_ss_pin=None):
        if sys.implementation.name in 'micropython' and sys.platform in 'rp2':
            # Raspberry Pi PR2040
            print("Hello RP2040")
            self.spi_type = 'rp2'
            assert spi_ss_pin is not None, "SPI(spi_ss_pin) needs to be defined"

            from machine import SPI, Pin
            self._spi = SPI(spi_id)
            self._spi.init(baudrate=baud_rate)
            self._spi_ss_pin = Pin(spi_ss_pin, Pin.OUT)
            self._spi_ss_pin.value(1)
        elif sys.implementation.name in 'cpython' and sys.implementation._multiarch in 'arm-linux-gnueabihf':
            # Raspberry Pi
            print("Hello RPi!")
            self.spi_type = 'spidev'
            from spidev import SpiDev
            self._spi = SpiDev()
            self._spi.open(spi_id, 0)
            self._spi.max_speed_hz = baud_rate
        elif sys.implementation.name in 'cpython' and sys.platform in 'darwin':
            # MacOS
            print("Hello Mac!")
            self.spi_type = 'spidriver'
            from spidriver import SPIDriver
            global global_spidriver
            if global_spidriver is None:
                global_spidriver = SPIDriver("/dev/tty.usbserial-DO01HFG1")
            self._spi = global_spidriver
            self._spi.unsel()
        else:
            print("Unsupported platform")
            self.spi_type = 'unknown'

    def __del__(self):
        """Cleanup function"""
        if self.spi_type == 'rp2':
            pass
        elif self.spi_type == 'spidev':
            pass
        elif self.spi_type in 'spidriver':
            self._spi.unsel()

    def transfer(self, write_data):
        """Transfer 'write_data' to SPI device, returns read_data"""
        if self.spi_type in 'rp2':
            read_buf = bytearray(len(write_data))
            self._spi_ss_pin.value(0)
            self._spi.write_readinto(bytearray(write_data), read_buf)
            self._spi_ss_pin.value(1)
            return bytes(read_buf)
        elif self.spi_type in 'spidriver':
            self._spi.sel()
            read_data = self._spi.writeread(write_data)
            self._spi.unsel()
            return read_data
        elif self.spi_type in 'spidev':
            response = self._spi.xfer(data)
            return bytes(response)


class Pin:
    IN = 0
    OUT = 1

    def __init__(self, pin_nr, direction=OUT):
        if sys.implementation.name in 'micropython' and sys.platform in 'rp2':
            # Raspberry Pi PR2040
            print("Hello RP2040")
            self.pin_type = 'rp2'
            from machine import Pin as MachinePin
            if direction == Pin.OUT:
                self._pin = MachinePin(pin_nr, MachinePin.OUT)
            else:
                self._pin = MachinePin(pin_nr, MachinePin.IN)
            self._pin.value(0)
        elif sys.implementation.name in 'cpython' and sys.implementation._multiarch in 'arm-linux-gnueabihf':
            # Raspberry Pi
            print("Hello RPi!")
            self.pin_type = 'rpi'
            import RPi.GPIO as GPIO
            self._gpio = GPIO
            self._gpio.setmode(GPIO.BCM)
            self._gpio.setup(pin_nr, GPIO.OUT)
            self._pin_nr = pin_nr
        elif sys.implementation.name in 'cpython' and sys.platform in 'darwin':
            # MacOS
            print("Hello Mac!")
            self.pin_type = 'spidriver'
            assert pin_nr <= 1, "Pin(pin_nr) only supports pin_nr = 0 and 1 for SPIDriver"
            from spidriver import SPIDriver
            global global_spidriver
            if global_spidriver is None:
                global_spidriver = SPIDriver("/dev/tty.usbserial-DO01HFG1")
            if pin_nr == 0:
                self._pin = global_spidriver.seta
            else:
                self._pin = global_spidriver.setb
        else:
            print("Unsupported platform")
            self.pin_type = 'unknown'

    def __del__(self):
        """Cleanup function"""
        if self.pin_type == 'spidev':
            self._gpio.cleanup()

    def output(self, set_value):
        """Set pin output value"""
        if self.pin_type == 'rp2':
            self._pin(set_value)
        elif self.pin_type == 'spidev':
            self._gpio.output(self._pin_nr, set_value)
        elif self.pin_type in 'spidriver':
            self._pin(set_value)
