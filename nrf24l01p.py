from icecream import ic


class NRF24L01P:
    # RF output power levels
    PWR_MIN = 0x0
    PWR_LOW = 0x1
    PWR_HIGH = 0x2
    PWR_MAX = 0x3

    # Data rates
    DR_250KBPS = 1 << 5 | 0 << 3
    DR_1MBPS = 0 << 5 | 0 << 3
    DR_2MBPS = 0 << 5 | 1 << 3

    # CRC
    CRC_DISABLED = 0x0
    CRC_8 = 0x02
    CRC_16 = 0x04
    CRC_ENABLED = 0x08

    # Registers
    CONFIG = 0x00
    EN_AA = 0x01
    EN_RXADDR = 0x02
    SETUP_AW = 0x03
    SETUP_RETR = 0x04
    RF_CH = 0x05
    RF_SETUP = 0x06
    STATUS = 0x07
    OBSERVE_TX = 0x08
    RPD = 0x09
    RX_ADDR_P0 = 0x0A
    RX_ADDR_P1 = 0x0B
    RX_ADDR_P2 = 0x0C
    RX_ADDR_P3 = 0x0D
    RX_ADDR_P4 = 0x0E
    RX_ADDR_P5 = 0x0F
    TX_ADDR = 0x10
    RX_PW_P0 = 0x11
    RX_PW_P1 = 0x12
    RX_PW_P2 = 0x13
    RX_PW_P3 = 0x14
    RX_PW_P4 = 0x15
    RX_PW_P5 = 0x16
    FIFO_STATUS = 0x17
    DYNPD = 0x1C
    FEATURE = 0x1D

    # *** Bit Mnemonics ***
    # CONFIG register register bits
    MASK_RX_DR = 1 << 7
    MASK_TX_DS = 1 << 5
    MASK_MAX_RT = 1 << 4
    EN_CRC = 1 << 3
    CRC0 = 1 << 2
    PWR_UP = 1 << 1
    PRIM_RX = 1 << 0

    # SETUP_RETR register bits
    ARD = 1 << 4
    ARC = 1 << 0

    # RF_SETUP register bits
    CONT_WAVE = 1 << 7
    RF_DR_LOW = 1 << 5
    PLL_LOCK = 1 << 4
    RF_DR_HIGH = 1 << 3
    RF_PWR = 1 << 1

    # EN_AA register bits
    ENAA_P0 = 1 << 0
    ENAA_P1 = 1 << 1
    ENAA_P2 = 1 << 2
    ENAA_P3 = 1 << 3
    ENAA_P4 = 1 << 4
    ENAA_P5 = 1 << 5

    # EN_RXADDR register bits
    ERX_P0 = 1 << 0
    ERX_P1 = 1 << 1
    ERX_P2 = 1 << 2
    ERX_P3 = 1 << 3
    ERX_P4 = 1 << 4
    ERX_P5 = 1 << 5

    # STATUS register bits
    RX_DR = 1 << 5
    TX_DS = 1 << 5
    MAX_RT = 1 << 4
    RX_P_NO = 1 << 1
#    TX_FULL = 1 << 0

    # OBSERVE_TX register bits
    PLOS_CNT = 1 << 4
    ARC_CNT = 1 << 0

    # FIFO_STATUS register bits
    TX_REUSE = 1 << 6
    TX_FULL = 1 << 5
    TX_EMPTY = 1 << 4
    RX_FULL = 1 << 1
    RX_EMPTY = 1 << 0

    # DYNPD register bits
    DPL_P5 = 1 << 5
    DPL_P4 = 1 << 4
    DPL_P3 = 1 << 3
    DPL_P2 = 1 << 2
    DPL_P1 = 1 << 1
    DPL_P0 = 1 << 0

    # FEATURE register bits
    EN_DPL = 1 << 3
    EN_ACK_PAY = 1 << 2
    EN_DYN_ACK = 1 << 0

    # Instruction Mnemonics
    R_REGISTER = 0x00
    W_REGISTER = 0x20
    R_RX_PAYLOAD = 0x61
    W_TX_PAYLOAD = 0xA0
    FLUSH_TX = 0xE1
    FLUSH_RX = 0xE2
    REUSE_TX_PL = 0xE3
    R_RX_PL_WID = 0x60
    W_ACK_PAYLOAD = 0xA8
    W_TX_PAYLOAD_NO_ACK = 0xB0
    NOP = 0xFF

    def __init__(self, spi_transfer, ce_pin):
        self._spi_transfer = spi_transfer
        self._ce_pin = ce_pin
        self.payload_size = 16
        self.prim_rx = 0
        self.write_cmd(NRF24L01P.FLUSH_RX)
        self.write_cmd(NRF24L01P.FLUSH_TX)
        self.trx_enable(False)

    def read_cmd(self, cmd, length):
        response = self._spi_transfer(bytes([cmd]) + bytes(length))
        return response

    def write_cmd(self, cmd, data=None):
        if data is None:
            response = self._spi_transfer(bytes([cmd]))
        else:
            response = self._spi_transfer(bytes([cmd]) + data)
        return bytes([response[0]])

    def read_reg(self, reg, length):
        response = self._spi_transfer(bytes([NRF24L01P.R_REGISTER | reg]) + bytes(length))
        return response

    def write_reg(self, reg, data):
        response = self._spi_transfer(bytes([NRF24L01P.W_REGISTER | reg]) + data)
        return bytes([response[0]])

    def setup(self, prim_rx, mask_rx_dr=0, mask_tx_ds=0, mask_max_rt=0, en_crc=1, crc0=0, aw=0x3, ard=0x0,
              arc=0x3, rf_ch=2, rf_dr=DR_2MBPS, rf_pwr=PWR_MAX, payload_size=16):
        assert payload_size <= 32, "Maximum payload size is 32"
        self.payload_size = payload_size
        self.prim_rx = prim_rx
        response = self.read_reg(NRF24L01P.CONFIG, 1)
        pwr_up = response[1] & NRF24L01P.PWR_UP
        self.write_reg(NRF24L01P.CONFIG, bytes([mask_rx_dr * NRF24L01P.MASK_RX_DR |
                                                mask_tx_ds * NRF24L01P.MASK_TX_DS |
                                                mask_max_rt * NRF24L01P.MASK_MAX_RT |
                                                en_crc * NRF24L01P.EN_CRC |
                                                crc0 * NRF24L01P.CRC_8 |
                                                pwr_up |
                                                prim_rx * NRF24L01P.PRIM_RX]))
        self.write_reg(NRF24L01P.SETUP_AW, bytes([aw]))
        self.write_reg(NRF24L01P.RF_CH, bytes([rf_ch]))
        self.write_reg(NRF24L01P.RF_SETUP, bytes([rf_dr | rf_pwr * NRF24L01P.RF_PWR]))
        self.write_reg(NRF24L01P.SETUP_RETR, bytes([ard * NRF24L01P.ARD | arc * NRF24L01P.ARC]))

    def trx_enable(self, enable=True):
        if enable:
            self._ce_pin(1)
        else:
            self._ce_pin(0)

    def power_up(self, pwr_up=True):
        response = self.read_reg(NRF24L01P.CONFIG, 1)
        if pwr_up:
            data = response[1] | NRF24L01P.PWR_UP
        else:
            data = response[1] & ~NRF24L01P.PWR_UP
        self.write_reg(NRF24L01P.CONFIG, bytes([data]))

    def tx_addr(self, addr):
        self.write_reg(NRF24L01P.TX_ADDR, addr)

    def status(self):
        response = self.read_cmd(NRF24L01P.NOP, 0)
        return response

    def observe_tx(self):
        response = self.read_reg(NRF24L01P.OBSERVE_TX, 1)
        arc_cnt = response[1] & 0x0F
        plos_cnt = (response[1] & 0xF0) >> 4
        return arc_cnt, plos_cnt

    def send_data(self, data):
        pass
