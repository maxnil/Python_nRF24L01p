import sys
#from icecream import ic


class IoCtrl:
    def __init__(self):
        if sys.implementation.name == 'cpython':
            print("We are running on CPython")
            try:
                from spidev import SpiDev
                print("Successfully imported 'spidev', so we most likely running on a Raspberry Pi")
                self.spi_type = 'spidev'
                self._spi = SpiDev()
                self._spi.open(0, 0)
            except ModuleNotFoundError:
                print("Did not manage to import 'spidev', so we are most likely not running on a Raspberry Pi")
                try:
                    from spidriver import SPIDriver
                    print("Successfully imported 'SPIDriver', so we are most likely running on the Mac")
                    self.spi_type = 'spidriver'
                    self._spi = SPIDriver("/dev/tty.usbserial-DO01HFG1")
                    self._spi.unsel()
                except ModuleNotFoundError:
                    print("Did not manage to import 'SPIDriver' (or any other SPI controller), so we give up")
                    self._spi = None
        elif sys.implementation.name == 'micropython':
            print("We are running on MicroPython")
            from machine import SPI
            self.spi_type = 'micropython'
            self._spi = SPI()
        else:
            raise Exception(f"Unknown implementation: '{sys.implementation.name}'")

    def spi_transfer(self, data):
        if self.spi_type == 'spidriver':
            self._spi.sel()
            response = self._spi.writeread(data)
            self._spi.unsel()
            return response
        elif self.spi_type == 'spidev':
            return data
        else:  # Assume MicroPython
            return data
