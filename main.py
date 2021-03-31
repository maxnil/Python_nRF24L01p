from icecream import ic
from io_ctrl import IoCtrl
from nrf24l01p import NRF24L01P
import sys
import time


def print_fifo_status(nrf23):
    status, response = nrf23.read_reg(NRF24L01P.FIFO_STATUS, 1)
    print("FIFO_STATUS:")
    if response[0] & 1 << 6:
        print(" TX_REUSE")
    if response[0] & 1 << 5:
        print(" TX_FULL")
    if response[0] & 1 << 4:
        print(" TX_EMPTY")
    if response[0] & 1 << 1:
        print(" RX_FULL")
    if response[0] & 1 << 0:
        print(" RX_EMPTY")


def main(trx_mode='x'):
    rf_ch = 95

    io_ctrl = IoCtrl(a_pin=25)
    nrf24 = NRF24L01P(io_ctrl.spi_transfer, io_ctrl.a_pin)

#    while True:
#        print("CW on")
#        cw_mode(nrf24, rf_ch)
#        time.sleep(5)
#        print("CW off")
#        cw_mode(nrf24, off=True)
#        time.sleep(5)

    if trx_mode in 't' or (trx_mode in 'x' and sys.platform in 'darwin'):  # MacBook Pro
        ptx_mode(nrf24, rf_ch)
    else:  # Raspberry Pi or MicroPython
        prx_mode(nrf24, rf_ch)


# Carrier Detect more
# def cd_mode(nrf24, rf_ch):
#    pass


# Constant Wave output mode
def cw_mode(nrf24, rf_ch=127, off=False):
    if off:
        nrf24.trx_enable(False)
        return

    nrf24.write_reg(NRF24L01P.CONFIG, bytes([0b00000010]))  # PWR_UP
    time.sleep(0.002)
    nrf24.write_reg(NRF24L01P.RF_SETUP, bytes([NRF24L01P.CONT_WAVE | NRF24L01P.PLL_LOCK | NRF24L01P.RF_PWR * 3]))
    nrf24.write_reg(NRF24L01P.RF_CH, bytes([rf_ch]))
    nrf24.trx_enable()  # Enter 'Standby-II'


def prx_mode(nrf24, rf_ch):
    print("Receiver mode")

    nrf24.setup(rf_ch=rf_ch)
    nrf24.rx_mode()
    nrf24.power_up()  # Enter 'Standby-1'

    ic(nrf24.status())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())
    print_fifo_status(nrf24)

    nrf24.trx_enable()
    
    while True:
        status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)

        if not (fifo_status[0] & NRF24L01P.RX_EMPTY):
            rx_data, rx_p_no = nrf24.read_rx_data()
            print(f"RX #{rx_p_no} Data: {rx_data}")


def ptx_mode(nrf24, rf_ch):
    print("Transmitter mode")

    nrf24.setup(rf_ch=rf_ch)
    nrf24.tx_mode()
    nrf24.power_up()  # Enter 'Standby-1'

    ic(nrf24.status())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())
    print_fifo_status(nrf24)

    print("Write 16 byte (1)")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hello World!0123')
    print_fifo_status(nrf24)

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    time.sleep(0.1)

    print_fifo_status(nrf24)
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())

    print("Write 7 byte (2)")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hi all!')
    print_fifo_status(nrf24)

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    print_fifo_status(nrf24)
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())


if __name__ == '__main__':
    if len(sys.argv) == 1:
        trx = 'x'
    else:
        trx = sys.argv[1]
    main(trx)
