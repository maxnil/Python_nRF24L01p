import sys


# from icecream import ic


class IoCtrl:
    def __init__(self, spi_ss_pin, a_pin=None, b_pin=None):
        if sys.implementation.name == 'cpython':
            print("We are running on CPython")
            try:
                from spidev import SpiDev
                import RPi.GPIO as GPIO
                print("Successfully imported 'spidev', so we most likely running on a Raspberry Pi")
                self.spi_type = 'spidev'
                self._spi = SpiDev()
                self._spi.open(0, 0)
                self._gpio = GPIO
                self._gpio.setmode(GPIO.BOARD)
                if a_pin is not None:
                    self._gpio.setup(a_pin, GPIO.OUT)
                if b_pin is not None:
                    self._gpio.setup(b_pin, GPIO.OUT)
                self._a_pin = a_pin
                self._b_pin = b_pin
            except ModuleNotFoundError:
                print("Did not manage to import 'spidev', so we are most likely not running on a Raspberry Pi")
                try:
                    from spidriver import SPIDriver
                    print("Successfully imported 'SPIDriver', so we are most likely running on the Mac")
                    self.spi_type = 'spidriver'
                    self._spi = SPIDriver("/dev/tty.usbserial-DO01HFG1")
                    self._spi.unsel()
                except ModuleNotFoundError:
                    raise Exception("No SPI module found")
        elif sys.implementation.name == 'micropython':
            print("We are running on MicroPython")
            from machine import Pin, SPI
            self.spi_type = 'micropython'
            self._spi = SPI(1)
            self._spi_ss_pin = Pin(spi_ss_pin, Pin.OUT)
            if a_pin is not None:
                self._a_pin = Pin(a_pin, Pin.OUT)
            if b_pin is not None:
                self._b_pin = Pin(b_pin, Pin.OUT)
        else:
            raise Exception(f"Unknown implementation: '{sys.implementation.name}'")

    def spi_transfer(self, data):
        if self.spi_type == 'spidriver':
            self._spi.sel()
            response = self._spi.writeread(data)
            self._spi.unsel()
            return response
        elif self.spi_type == 'spidev':
            response = self._spi.xfer(data)
            return response
        else:  # Assume MicroPython
            return data

    def a_pin(self, val):
        if self._a_pin is None:
            raise Exception("a_pin not configured")
        if self.spi_type == 'spidriver':
            self._spi.seta(val)
        elif self.spi_type == 'spidev':
            self._gpio.output(self._a_pin, val)
        else:  # Assume MicroPython
            self._a_pin.value(val)

    def b_pin(self, val):
        if self._b_pin is None:
            raise Exception("b_pin not configured")
        if self.spi_type == 'spidriver':
            self._spi.setb(val)
        elif self.spi_type == 'spidev':
            self._gpio.output(self._b_pin, val)
        else:  # Assume MicroPython
            self._b_pin.value(val)
