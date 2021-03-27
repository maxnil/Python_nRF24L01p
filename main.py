import sys
from io_ctrl import IoCtrl


def main():
    io_ctrl = IoCtrl()

    print("SPI Type", io_ctrl.spi_type)
    print(sys.version)

    resp = io_ctrl.spi_transfer(b'\x01\x13')
    print(resp)


if __name__ == '__main__':
    main()
