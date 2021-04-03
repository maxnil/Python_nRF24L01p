from icecream import ic
from io_peripheral import Pin, SPI
from nrf24l01p import NRF24L01P

import time


def main():
    rf_ch = 95

    spi = SPI()
    ce_pin = Pin(0, Pin.OUT)

    nrf24 = NRF24L01P(spi, ce_pin)

    ptx_mode(nrf24, rf_ch)


def prx_mode(nrf24, rf_ch):
    print("Receiver mode")

    nrf24.setup(rf_ch=rf_ch)
    nrf24.rx_mode()
    nrf24.power_up()  # Enter 'Standby-1'

    ic(nrf24.status())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())
    ic(nrf24.fifo_status_string())

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
    ic(nrf24.fifo_status_string())

    print("Write 16 byte (1)")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hello World!0123')
    ic(nrf24.fifo_status_string())

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    time.sleep(0.1)

    ic(nrf24.fifo_status_string())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())

    print("Write 7 byte (2)")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hi all!')
    ic(nrf24.fifo_status_string())

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    time.sleep(0.1)
    ic(nrf24.fifo_status_string())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())


if __name__ == '__main__':
    main()
