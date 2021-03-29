import sys


# from icecream import ic


class IoCtrl:
    def __init__(self, spi_ss_pin=None, a_pin=None, b_pin=None):
        if sys.implementation.name == 'cpython':
            try:
                from spidev import SpiDev
                import RPi.GPIO as GPIO
                self.spi_type = 'spidev'
                self._spi = SpiDev()
                self._spi.open(0, 0)
                self._spi.max_speed_hz = 10000000
                self._spi.mode = 0b00
                self._gpio = GPIO
                self._gpio.setmode(GPIO.BCM)
                if a_pin is not None:
                    self._gpio.setup(a_pin, GPIO.OUT)
                if b_pin is not None:
                    self._gpio.setup(b_pin, GPIO.OUT)
                self._a_pin = a_pin
                self._b_pin = b_pin
            except ModuleNotFoundError:
                try:
                    from spidriver import SPIDriver
                    self.spi_type = 'spidriver'
                    self._spi = SPIDriver("/dev/tty.usbserial-DO01HFG1")
                    self._spi.unsel()
                    self._spi.seta(0)
                    self._spi.setb(0)
                    self._a_pin = a_pin
                    self._b_pin = b_pin
                except ModuleNotFoundError:
                    raise Exception("No SPI module found")
        elif sys.implementation.name == 'micropython':
            from machine import Pin, SPI
            self.spi_type = 'micropython'
            self._spi = SPI(1, baudrate=10000000)
            self._spi_ss_pin = Pin(spi_ss_pin, Pin.OUT)
            if a_pin is not None:
                self._a_pin = Pin(a_pin, Pin.OUT)
            if b_pin is not None:
                self._b_pin = Pin(b_pin, Pin.OUT)
        else:
            raise Exception(f"Unknown implementation: '{sys.implementation.name}'")

        print("SPI type:", self.spi_type)

    def __del__(self):
        if self.spi_type == 'spidev':
            self._gpio.cleanup()

    def spi_transfer(self, data):
        if self.spi_type == 'spidriver':
            self._spi.sel()
            response = self._spi.writeread(data)
            self._spi.unsel()
            return bytes(response)
        elif self.spi_type == 'spidev':
            response = self._spi.xfer(data)
            return bytes(response)
        else:  # Assume MicroPython
            response = data
            self._spi.write_readinto(data, response)
            return bytes(response)

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
