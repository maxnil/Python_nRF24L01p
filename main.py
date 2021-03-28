import sys
from icecream import ic
from io_ctrl import IoCtrl


def main():
    io_ctrl = IoCtrl(25)

    print("SPI Type", io_ctrl.spi_type)
    print(sys.version)

    ic(io_ctrl.spi_transfer(b'\x01\x13')[1])


if __name__ == '__main__':
    main()
