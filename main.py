from icecream import ic
from io_ctrl import IoCtrl


def main():
    io_ctrl = IoCtrl(25)

    ic(io_ctrl.spi_transfer(b'\x00\x00'))
    ic(io_ctrl.spi_transfer(b'\x01\x00'))
    ic(io_ctrl.spi_transfer(b'\x02\x00'))
    ic(io_ctrl.spi_transfer(b'\x03\x00'))
    ic(io_ctrl.spi_transfer(b'\x04\x00'))
    ic(io_ctrl.spi_transfer(b'\x05\x00'))
    ic(io_ctrl.spi_transfer(b'\x06\x00'))
    ic(io_ctrl.spi_transfer(b'\x07\x00'))


if __name__ == '__main__':
    main()
