"""This is a MicroPython 'machine' compatible wrapper for Raspberry Pi I2C, SPI and Pin"""
from spidev import SpiDev
import RPi.GPIO as GPIO


class SPI:
    """SPI class that mimics MicroPython SPI class using a SPIDriver USB Dongle"""
    def __init__(self, spi_id=0, baudrate=1000000, polarity=0, phase=0):
        self._spidev = SpiDev()
        self._spidev.open(spi_id, 0)
        self._spidev.max_speed_hz = baudrate
        self._spidev.mode = polarity << 1 | phase

    def read(self, nbytes, write=0):
        return self._spidev.xfer(bytearray([write] * nbytes))

    def readint(self, buf, write=0):
        buf[:] = self._spidev.xfer(bytearray([write] * len(buf)))

    def write(self, buf):
        self._spidev.writebytes(buf)

    def write_readinto(self, write_buf, read_buf):
        read_buf[:] = self._spidev.xfer(write_buf)


class Pin:
    """SPI class that mimics MicroPython SPI class using a SPIDriver USB Dongle"""
    IN = 0
    OUT = 1

    def __init__(self, id, mode=-1, pull=-1):
        self._gpio = GPIO
        self._gpio.setmode(GPIO.BCM)
        self._gpio.setup(id, GPIO.OUT if mode == Pin.IN else GPIO.IN)
        self._pin_id = id

    def value(self, x=None):
        if x is None:
            return self._gpio.input(self._pin_id)
        else:
            self._gpio.output(x)

    def __call__(self, x=None):
        self.value(x)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def low(self):
        self.value(0)

    def high(self):
        self.value(1)
