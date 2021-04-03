# from icecream import ic


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

    # SETUP_AW register bits
    AW3 = 1 << 0
    AW4 = 2 << 0
    AW5 = 3 << 0

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
    EN_DPL = 1 << 2
    EN_ACK_PAY = 1 << 1
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

    def __init__(self, spi, ce_pin):
        """Initialize NRF24L01P (HW) object"""
        self._spi = spi
        self._ce_pin = ce_pin
        self.prim_rx = 0
        # Flush FIFOs, clear any pending interrupts and Power Down
        self.write_cmd(NRF24L01P.FLUSH_RX)
        self.write_cmd(NRF24L01P.FLUSH_TX)
        self.write_reg(NRF24L01P.STATUS, bytes([NRF24L01P.RX_DR | NRF24L01P.TX_DS | NRF24L01P.MAX_RT]))
        self.trx_disable()
        status, config = self.read_reg(NRF24L01P.CONFIG, 1)
        self.write_reg(NRF24L01P.CONFIG, bytes([config[0] & ~NRF24L01P.PWR_UP]))

    def read_cmd(self, cmd, length):
        """Read Command and return NRF24L01P status (int), command data (bytes)"""
        response = self._spi.transfer(bytes([cmd]) + bytes(length))
        if length == 0:
            return response[0], b''
        else:
            return response[0], response[1:]

    def write_cmd(self, cmd, data=b''):
        """Write Command and return NRF24L01P status (int)"""
        response = self._spi.transfer(bytes([cmd]) + data)
        return response[0]

    def read_reg(self, reg, length):
        """Read Register and return NRF24L01P status (int), register data (bytes)"""
        response = self._spi.transfer(bytes([NRF24L01P.R_REGISTER | reg]) + bytes(length))
        return response[0], response[1:]

    def write_reg(self, reg, data):
        """Write Register and return NRF24L01P status (int)"""
        response = self._spi.transfer(bytes([NRF24L01P.W_REGISTER | reg]) + data)
        return response[0]

    def setup(self, mask_irq=0, rf_ch=2, rf_dr=DR_2MBPS, rf_pwr=PWR_MAX, erx=ERX_P0 | ERX_P1,
              rx_addr_p0=b'\xE7\xE7\xE7\xE7\xE7', rx_addr_p1=b'\xC2\xC2\xC2\xC2\xC2', rx_addr_p2=b'\xC3',
              rx_addr_p3=b'\xC4', rx_addr_p4=b'\xC5', rx_addr_p5=b'\xC6', tx_addr=b'\xE7\xE7\xE7\xE7\xE7'):
        """Setup NRF24L01P. Should be run first.
        Configuration:
          2 byte CRC
          5 byte address
          250 us resend wait time
          15 resend retries
          Auto acknowledge (on all pipes)
          Dynamic Payload Length (on all pipes)
        """
        self.write_reg(NRF24L01P.CONFIG, bytes([mask_irq | NRF24L01P.EN_CRC | NRF24L01P.CRC0]))
        self.write_reg(NRF24L01P.EN_AA, bytes([NRF24L01P.ENAA_P0 | NRF24L01P.ENAA_P1 | NRF24L01P.ENAA_P2 |
                                               NRF24L01P.ENAA_P3 | NRF24L01P.ENAA_P4 | NRF24L01P.ENAA_P5]))
        self.write_reg(NRF24L01P.SETUP_AW, bytes([NRF24L01P.AW5]))
        self.rf_channel(rf_ch)
        self.write_reg(NRF24L01P.RF_SETUP, bytes([rf_dr | rf_pwr * NRF24L01P.RF_PWR]))
        self.write_reg(NRF24L01P.SETUP_RETR, bytes([0x0F]))  # Wait 250 ua, 15 retries
        self.write_reg(NRF24L01P.FEATURE, bytes([NRF24L01P.EN_DPL]))
        self.write_reg(NRF24L01P.DYNPD, bytes([NRF24L01P.DPL_P0 | NRF24L01P.DPL_P1 | NRF24L01P.DPL_P2 |
                                               NRF24L01P.DPL_P3 | NRF24L01P.DPL_P4 | NRF24L01P.DPL_P5]))
        self.write_reg(NRF24L01P.RX_ADDR_P0, rx_addr_p0)
        self.write_reg(NRF24L01P.RX_ADDR_P1, rx_addr_p1)
        self.write_reg(NRF24L01P.RX_ADDR_P2, rx_addr_p2)
        self.write_reg(NRF24L01P.RX_ADDR_P3, rx_addr_p3)
        self.write_reg(NRF24L01P.RX_ADDR_P4, rx_addr_p4)
        self.write_reg(NRF24L01P.RX_ADDR_P5, rx_addr_p5)
        self.write_reg(NRF24L01P.EN_RXADDR, bytes([erx]))
        self.write_reg(NRF24L01P.TX_ADDR, tx_addr)

    def rf_channel(self, rf_ch):
        """Set RF channel (0-127)"""
        assert rf_ch <= 127, "RF Channel out of range"
        self.write_reg(NRF24L01P.RF_CH, bytes([rf_ch]))

    def rx_mode(self):
        """Set RX Mode"""
        self.prim_rx = 1
        status, config = self.read_reg(NRF24L01P.CONFIG, 1)
        self.write_reg(NRF24L01P.CONFIG, bytes([config[0] | NRF24L01P.PRIM_RX]))

    def tx_mode(self):
        """Set TX Mode"""
        self.prim_rx = 0
        status, config = self.read_reg(NRF24L01P.CONFIG, 1)
        self.write_reg(NRF24L01P.CONFIG, bytes([config[0] & ~NRF24L01P.PRIM_RX]))

    def trx_enable(self):
        """Enable RX/TX Mode"""
        self._ce_pin.output(1)

    def trx_disable(self):
        """Disable RX/TX Mode"""
        self._ce_pin.output(0)

    def power_up(self,):
        """Power Up device (go to Standby-I state)"""
        status, config = self.read_reg(NRF24L01P.CONFIG, 1)
        self.write_reg(NRF24L01P.CONFIG, bytes([config[0] | NRF24L01P.PWR_UP]))

    def power_down(self):
        """Power Down device (go to Power Down state)"""
        status, config = self.read_reg(NRF24L01P.CONFIG, 1)
        self.write_reg(NRF24L01P.CONFIG, bytes([config[0] & ~NRF24L01P.PWR_UP]))

    def tx_addr(self, addr):
        """Set TX Address"""
        self.write_reg(NRF24L01P.TX_ADDR, addr)

    def status(self):
        """NRF24L01P status returns current status (int)"""
        return self.read_cmd(NRF24L01P.NOP, 0)[0]

    def lost_pkg_count(self):
        """Lost Packet Count, returns number of packets that has been lost since previous call"""
        status, observe_tx = self.read_reg(NRF24L01P.OBSERVE_TX, 1)
        plos_cnt = (observe_tx[0] & 0xF0) >> 4
        status, rf_ch = self.read_reg(NRF24L01P.RF_CH, 1)
        self.write_reg(NRF24L01P.RF_CH, rf_ch)  # Clear PLOS_CNT
        return plos_cnt

    def retransmit_count(self):
        """Retransmit Count, returns number of retransmissions (saturates at 15)"""
        status, observe_tx = self.read_reg(NRF24L01P.OBSERVE_TX, 1)
        arc_cnt = observe_tx[0] & 0x0F
        self.write_reg(NRF24L01P.STATUS, bytes([NRF24L01P.MAX_RT]))  # Clear MAX_RT interrupt (if any)
        return arc_cnt

    def write_tx_data(self, data):
        """Write Data to TX FIFO, returns False if TX_FIFO is full, otherwise it returns True"""
        assert len(data) <= 32, "Data length is out of range"

        if self.status() & 0x01:
            return False  # TX FIFO full

        self.write_cmd(NRF24L01P.W_TX_PAYLOAD, data)
        return True

    def read_rx_data(self):
        """Read Data from RX FIFO, returns RX Data and Pipe number"""
        status, rx_pl_wid = self.read_cmd(NRF24L01P.R_RX_PL_WID, 1)
        rx_p_no = (status >> 1) & 0x07
        if rx_p_no == 0x7:
            rx_data = None
        else:
            status, rx_data = self.read_cmd(NRF24L01P.R_RX_PAYLOAD, rx_pl_wid[0])
        return rx_data, rx_p_no

    def fifo_status_string(self):
        status, response = self.read_reg(NRF24L01P.FIFO_STATUS, 1)
        status_str = ""
        if response[0] & 1 << 6:
            status_str += "TX_REUSE,"
        if response[0] & 1 << 5:
            status_str += "TX_FULL,"
        if response[0] & 1 << 4:
            status_str += "TX_EMPTY,"
        if response[0] & 1 << 1:
            status_str += "RX_FULL,"
        if response[0] & 1 << 0:
            status_str += "RX_EMPTY,"
        return status_str
