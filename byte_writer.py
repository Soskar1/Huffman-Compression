import logging

class ByteWriter(object):
    def __init__(self):
        self.m_buffer: bytearray = bytearray()
        self.m_currentByte: int = 0b0
        self.m_maxBits: int = 8
        self.m_leftToWriteBits: int = 8

        self.m_logger: logging.Logger = logging.getLogger(__name__)

    def UpdateBuffer(self):
        self.m_buffer.append(self.m_currentByte)
        self.m_logger.debug(f"Appended {self.m_currentByte:08b} to buffer. Current buffer {self.m_buffer}")
        
        self.m_currentByte = 0b0
        self.m_leftToWriteBits = self.m_maxBits
    
    def WriteBit(self, bit: int) -> int:
        if bit != 0 and bit != 1:
            return -1

        if bit == 1:
            if self.m_leftToWriteBits == 8:
                self.m_currentByte |= 0b10000000
            if self.m_leftToWriteBits == 7:
                self.m_currentByte |= 0b1000000
            if self.m_leftToWriteBits == 6:
                self.m_currentByte |= 0b100000
            if self.m_leftToWriteBits == 5:
                self.m_currentByte |= 0b10000
            if self.m_leftToWriteBits == 4:
                self.m_currentByte |= 0b1000
            if self.m_leftToWriteBits == 3:
                self.m_currentByte |= 0b100
            if self.m_leftToWriteBits == 2:
                self.m_currentByte |= 0b10
            if self.m_leftToWriteBits == 1:
                self.m_currentByte |= 0b1
        
        self.m_leftToWriteBits -= 1
        self.m_logger.debug(f"Wrote {str(bit)} bit. Current byte = {self.m_currentByte:08b}. leftToWriteBits = {self.m_leftToWriteBits}")

        if self.m_leftToWriteBits == 0:
            self.UpdateBuffer()

        return 1

    def WriteByte(self, byte: int) -> None:
        self.m_logger.debug(f'Trying to write "{chr(byte)}" ({byte:08b}). leftToWriteBits={self.m_leftToWriteBits}')

        if self.m_leftToWriteBits == self.m_maxBits:
            self.m_currentByte = byte
            self.UpdateBuffer()
        else:
            for bitPosition in range(8):
                bit: int = self.GetBitAtPosition(byte, bitPosition)
                self.WriteBit(bit)
    
    def GetBitAtPosition(self, byte: int, position: int) -> int:
        if position == 0:
            return 1 if byte & 0b10000000 == 0b10000000 else 0
        if position == 1:
            return 1 if byte & 0b1000000 == 0b1000000 else 0
        if position == 2:
            return 1 if byte & 0b100000 == 0b100000 else 0
        if position == 3:
            return 1 if byte & 0b10000 == 0b10000 else 0
        if position == 4:
            return 1 if byte & 0b1000 == 0b1000 else 0
        if position == 5:
            return 1 if byte & 0b100 == 0b100 else 0
        if position == 6:
            return 1 if byte & 0b10 == 0b10 else 0
        if position == 7:
            return 1 if byte & 0b1 == 0b1 else 0