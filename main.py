from icecream import ic
from io_ctrl import IoCtrl
from nrf24l01p import NRF24L01P
import sys
import time


def print_fifo_status(nrf23):
    response = nrf23.read_reg(NRF24L01P.FIFO_STATUS, 1)[1]
    print("FIFO_STATUS:")
    if response & 1 << 6:
        print(" TX_REUSE")
    if response & 1 << 5:
        print(" TX_FULL")
    if response & 1 << 4:
        print(" TX_EMPTY")
    if response & 1 << 1:
        print(" RX_FULL")
    if response & 1 << 0:
        print(" RX_EMPTY")


def main():
    payload_size = 16
    rf_ch = 64

    io_ctrl = IoCtrl(a_pin=25)
    nrf24 = NRF24L01P(io_ctrl.spi_transfer, io_ctrl.a_pin)

    if sys.platform in 'darwin':  # MacBook Pro
        ptx_mode(nrf24, rf_ch, payload_size)
    else:  # Raspberry Pi or MicroPython
        prx_mode(nrf24, rf_ch, payload_size)


def prx_mode(nrf24, rf_ch, payload_size):
    print("Receiver mode")

#    nrf24.setup(prim_rx=1, rf_ch=rf_ch, payload_size=payload_size)

    ic(nrf24.read_reg(NRF24L01P.STATUS, 1))
    ic(nrf24.read_reg(NRF24L01P.OBSERVE_TX, 1))
    print_fifo_status(nrf24)
    print("Configure 'all' registers")
    nrf24.write_cmd(NRF24L01P.FLUSH_RX)
    nrf24.write_cmd(NRF24L01P.FLUSH_TX)
    nrf24.write_reg(NRF24L01P.STATUS, bytes([0b01110000]))  # Clear any pending interrupts
    nrf24.write_reg(NRF24L01P.CONFIG, bytes([0b01111111]))  # PRX
    nrf24.write_reg(NRF24L01P.EN_AA, bytes([0b00111111]))
    nrf24.write_reg(NRF24L01P.EN_RXADDR, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.SETUP_AW, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.SETUP_RETR, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.RF_CH, bytes([2]))
    nrf24.write_reg(NRF24L01P.RF_SETUP, bytes([0b00001110]))
    ic(nrf24.read_reg(NRF24L01P.STATUS, 1))
    ic(nrf24.read_reg(NRF24L01P.OBSERVE_TX, 1))
    print_fifo_status(nrf24)
    ic(nrf24.read_reg(NRF24L01P.RX_ADDR_P0, 5))
    ic(nrf24.read_reg(NRF24L01P.TX_ADDR, 5))
    ic(nrf24.read_reg(NRF24L01P.DYNPD, 1))
    ic(nrf24.read_reg(NRF24L01P.FEATURE, 1))

#    nrf24.power_up()  # Enter 'Standby-1'
    nrf24.trx_enable()

    ic(nrf24.status())
    ic(nrf24.read_reg(NRF24L01P.CONFIG, 1))

    for i in range(5):
        print_fifo_status(nrf24)
        ic(nrf24.read_reg(NRF24L01P.RX_PW_P0, 1))
        time.sleep(1)


def ptx_mode(nrf24, rf_ch, payload_size):
    print("Transmitter mode")

    nrf24.setup(prim_rx=0, rf_ch=rf_ch, payload_size=payload_size, arc=15)

    ic(nrf24.read_reg(NRF24L01P.STATUS, 1))
    ic(nrf24.read_reg(NRF24L01P.OBSERVE_TX, 1))
    print_fifo_status(nrf24)
    print("Configure 'all' registers")
    nrf24.write_cmd(NRF24L01P.FLUSH_RX)
    nrf24.write_cmd(NRF24L01P.FLUSH_TX)
    nrf24.write_reg(NRF24L01P.STATUS, bytes([0b01110000]))  # Clear any pending interrupts
    nrf24.write_reg(NRF24L01P.CONFIG, bytes([0b01111110]))  # TRX
    nrf24.write_reg(NRF24L01P.EN_AA, bytes([0b00111111]))
    nrf24.write_reg(NRF24L01P.EN_RXADDR, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.SETUP_AW, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.SETUP_RETR, bytes([0b00000011]))
    nrf24.write_reg(NRF24L01P.RF_CH, bytes([2]))
    nrf24.write_reg(NRF24L01P.RF_SETUP, bytes([0b00001110]))
    ic(nrf24.read_reg(NRF24L01P.STATUS, 1))
    ic(nrf24.read_reg(NRF24L01P.OBSERVE_TX, 1))
    print_fifo_status(nrf24)
    ic(nrf24.read_reg(NRF24L01P.RX_ADDR_P0, 5))
    ic(nrf24.read_reg(NRF24L01P.TX_ADDR, 5))
    ic(nrf24.read_reg(NRF24L01P.DYNPD, 1))
    ic(nrf24.read_reg(NRF24L01P.FEATURE, 1))

#    nrf24.power_up()  # Enter 'Standby-1'

    ic(nrf24.status())

    print_fifo_status(nrf24)

    print("Write 32 byte #1")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hello World!  1 ')
    print_fifo_status(nrf24)
#    print("Write 32 byte #2")
#    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD_NO_ACK, b'12345678901234567890123456789012')
#    print_fifo_status(nrf24)
#    print("Write 32 byte #3")
#    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD_NO_ACK, b'abcdefghijklmnopqrstuvwxyz')
#    print_fifo_status(nrf24)

    ic(nrf24.observe_tx())

    nrf24.trx_enable()  # Enter 'Standby-II'
    time.sleep(1)
    print_fifo_status(nrf24)
    ic(nrf24.observe_tx())


if __name__ == '__main__':
    main()
