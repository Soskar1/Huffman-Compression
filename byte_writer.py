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
            self.m_currentByte |= (0b1 << (self.m_leftToWriteBits - 1))
        
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
                bit: int = self.GetBitAtPosition(byte, bitPosition, self.m_maxBits)
                self.WriteBit(bit)
    
    def GetBitAtPosition(self, byte: int, position: int, maxBits: int) -> int:
        return (byte >> (maxBits - 1 - position)) & 0b1
    
    def WriteBitsFromByte(self, byte: int, bitsToWrite: int) -> None:
        self.m_logger.debug(f"Trying to write {bitsToWrite} bits from {byte:08b}")
        
        for bitPosition in range(bitsToWrite):
            bit: int = self.GetBitAtPosition(byte, bitPosition, bitsToWrite)
            self.WriteBit(bit)
    
    def PopContent(self, getAll: bool = False) -> bytearray:
        if self.m_leftToWriteBits == self.m_maxBits or getAll:
            content = bytearray(self.m_buffer)
            self.m_buffer.clear()
            return content
        
        lastIndex = len(self.m_buffer) - 1
        content = self.m_buffer[:lastIndex]
        self.m_buffer = bytearray([self.m_buffer[lastIndex]])
        return content