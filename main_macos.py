from icecream import ic
from machine_dongle import Pin, SPI
from nrf24l01p import NRF24L01P

import time


def main():
    rf_ch = 95

    spi = SPI()
    ce_pin = Pin(0, Pin.OUT)

    nrf24 = NRF24L01P(spi, ce_pin)

    #cd_mode(nrf24)

    ptx_mode(nrf24, rf_ch)


def cw_mode(nrf24):
    print("Constant Wave Mode")

    nrf24.setup(rf_ch=95)
    nrf24.write_cmd(NRF24L01P.CONFIG, bytes([NRF24L01P.PWR_UP]))
    nrf24.write_cmd(NRF24L01P.RF_SETUP, bytes([NRF24L01P.CONT_WAVE | NRF24L01P.PLL_LOCK | NRF24L01P.RF_PWR * 3]))
    time.sleep(0.1)
    nrf24.trx_enable()  # Enable transmitter
    print("Constant Wave is on")


def cw_off(nrf24):
    nrf24.trx_disable()  # Disable transmitter
    nrf24.write_cmd(NRF24L01P.CONFIG, bytes([0x00]))
    print("Constant Wave is off")


def cd_mode(nrf24):
    print("Carrier Detect Mode")
    nrf24.write_reg(NRF24L01P.CONFIG, bytes([NRF24L01P.PWR_UP | NRF24L01P.PRIM_RX]))
    nrf24.write_reg(NRF24L01P.EN_AA, b'\x00')
    nrf24.write_reg(NRF24L01P.EN_RXADDR, b'\x00')
    nrf24.write_reg(NRF24L01P.RF_CH, b'\x00')
    time.sleep(0.1)
    nrf24.write_reg(NRF24L01P.RF_SETUP, b'\x00')
    time.sleep(0.1)
    nrf24.trx_enable()  # Enable receiver
    while True:
        for rf_ch in range(128):
            i = 0
            nrf24.write_reg(NRF24L01P.RF_CH, bytes([rf_ch]))
            for t in range(100):
                status, rdp = nrf24.read_reg(NRF24L01P.RPD, 1)
                i += rdp[0]
            print("rf_ch = ", rf_ch, " RDP = ", i)


def prx_mode(nrf24, rf_ch):
    print("Receiver mode")

    nrf24.setup(rf_ch=rf_ch)
    nrf24.rx_mode()
    nrf24.power_up()  # Enter 'Standby-1'

    ic(nrf24.status())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())
    ic(nrf24.fifo_status_string())

    nrf24.trx_enable()  # Enable receiver
    
    while True:
        status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)

        status, rpd = nrf24.read_reg(NRF24L01P.RPD, 1)
        print("RPD: ", rpd)

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
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hello from MacBook Pro')
    ic(nrf24.fifo_status_string())

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    time.sleep(0.1)

    ic(nrf24.fifo_status_string())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())

    print("Write 7 byte (2)")
    nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, b'Hello from MacBook Pro again!')
    ic(nrf24.fifo_status_string())

    nrf24.trx_enable()  # Enter 'TX Mode'
    time.sleep(15e-6)  # Wait >10 us
    nrf24.trx_disable()  # Enter 'Standby-I'

    time.sleep(0.1)

    ic(nrf24.fifo_status_string())
    ic(nrf24.lost_pkg_count())
    ic(nrf24.retransmit_count())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Terminated by CTRL-C")
