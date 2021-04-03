"""
This is the main file for the Raspberry Pi Pico board
"""
from io_peripheral import Pin, SPI


def main():
    spi = SPI()

    ce_pin = Pin(0, Pin.OUT)

    print(spi.transfer(b'\x00\x00'))


if __name__ == '__main__':
    main()
