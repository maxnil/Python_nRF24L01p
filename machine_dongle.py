"""This is a MicroPython 'machine' compatible wrapper for I2CDevice I2C and SPIDevice SPI/Pin USB dongles"""
from spidriver import SPIDriver


global_spidrv = None


class SPI:
    """SPI class that mimics MicroPython SPI class using a SPIDriver USB Dongle"""
    def __init__(self, spi_id=0, baudrate=1000000, polarity=0, phase=0):
        global global_spidrv
        if global_spidrv is None:
            global_spidrv = SPIDriver("/dev/tty.usbserial-DO01HFG1")
        self._spidrv = global_spidrv

    def read(self, nbytes, write=0):
        self._spidrv.sel()
        response = self._spidrv.writeread(bytearray([write] * nbytes))
        self._spidrv.unsel()
        return response

    def readinto(self, buf, write=0):
        self._spidrv.sel()
        buf[:] = self._spidrv.writeread(bytearray([write] * len(buf)))
        self._spidrv.unsel()

    def write(self, buf):
        self._spidrv.sel()
        self._spidrv.write(buf)
        self._spidrv.unsel()

    def write_readinto(self, write_buf, read_buf):
        self._spidrv.sel()
        read_buf[:] = self._spidrv.writeread(write_buf)
        self._spidrv.unsel()


class Pin:
    """SPI class that mimics MicroPython SPI class using a SPIDriver USB Dongle"""
    IN = 0
    OUT = 1

    def __init__(self, id, mode=-1, pull=-1):
        assert id <= 1, "Pin only supports pin id = 0, 1 and 2 for SPIDriver"
        assert mode is Pin.OUT, "Pin only supports output for SPIDriver"
        global global_spidrv
        if global_spidrv is None:
            global_spidrv = SPIDriver("/dev/tty.usbserial-DO01HFG1")
        self._pin_id = id
        self._spidrv = global_spidrv

    def value(self, x=None):
        assert x is not None, "Pin only supports output for SPIDriver"
        if self._pin_id == 0:
            self._spidrv.seta(x)
        else:
            self._spidrv.setb(x)

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
