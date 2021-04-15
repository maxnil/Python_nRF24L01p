from icecream import ic
from machine_rpi import Pin, SPI
from nrf24l01p import NRF24L01P
import time


def main():
    rf_ch = 95

    spi = SPI()
    nrf24 = NRF24L01P(spi=spi, cs_pin=Pin(None), ce_pin=Pin(25, Pin.OUT))

    sender(nrf24, rf_ch)

    # ptx_mode(nrf24, rf_ch)


def sender(nrf24, rf_ch):
    power_range = ((NRF24L01P.PWR_MIN, "-18 dBm"),
                   (NRF24L01P.PWR_LOW, "-12 dBm"),
                   (NRF24L01P.PWR_HIGH, " -6 dBm"),
                   (NRF24L01P.PWR_MAX, "  0 dBm"))
    data_rate_range = ((NRF24L01P.DR_250KBPS, "250 Kbps"),
                       (NRF24L01P.DR_1MBPS, "  1 Mbps"),
                       (NRF24L01P.DR_2MBPS, "  2 Mbps"))
    nr_packets = 10  # Number of packets per iteration

    print("Sender")

    nrf24.setup(rf_ch=rf_ch)
    nrf24.tx_mode()
    nrf24.power_up()  # Enter 'Standby-1'

    data_rate, data_rate_str = data_rate_range[2]

    status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)
    while not fifo_status[0] & NRF24L01P.TX_EMPTY:
        status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)

    nrf24.data_rate(data_rate)

    for power, power_str in reversed(power_range):
        nrf24.tx_power(power)
        retransmit_count = list([0] * 16)
        lost_packet_count = 0

        for x in range(nr_packets):
            nrf24.rf_channel(rf_ch)  # Just to clear Lost packet counter
            packet_string = "Pkg Nr: %5s" % x + "; " + data_rate_str + "; " + power_str
            # print(len(packet_string), packet_string)
            nrf24.write_cmd(NRF24L01P.W_TX_PAYLOAD, bytes(packet_string, 'utf-8'))
            nrf24.trx_enable()  # Enter 'TX Mode'
            time.sleep(15e-6)  # Wait >10 us
            nrf24.trx_disable()  # Enter 'Standby-I'

            status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)
            while not fifo_status[0] & NRF24L01P.TX_EMPTY:
                status, fifo_status = nrf24.read_reg(NRF24L01P.FIFO_STATUS, 1)
            # ic(nrf24.lost_pkg_count())
            retransmit_count[(nrf24.retransmit_count())] += 1
            lost_packet_count += nrf24.lost_pkg_count()

        print("Power:", power_str)
        print("Retransmit Count :", retransmit_count)
        print("Lost packet count:", lost_packet_count)
        print("---")


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
