import logging

class ByteWriter(object):
    def __init__(self):
        self.m_buffer: bytearray = bytearray()
        self.m_currentByte: int = 0b0
        self.m_maxBits: int = 8
        self.m_leftToWriteBits: int = 8
        self.m_lastWriteBits: int = 0

        self.m_logger: logging.Logger = logging.getLogger(__name__)

    def UpdateBuffer(self):
        self.m_buffer.append(self.m_currentByte)
        self.m_logger.debug(f"Appended {self.m_currentByte:08b} to buffer. Buffer length: {len(self.m_buffer)}. Current buffer {self.m_buffer}")
        
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
        
        self.m_lastWriteBits = 8
    
    def GetBitAtPosition(self, byte: int, position: int, maxBits: int) -> int:
        return (byte >> (maxBits - 1 - position)) & 0b1
    
    def WriteBitsFromByte(self, byte: int, bitsToWrite: int) -> None:
        self.m_logger.debug(f"Trying to write {bitsToWrite} bits from {byte:08b}")
        
        for bitPosition in range(bitsToWrite):
            bit: int = self.GetBitAtPosition(byte, bitPosition, bitsToWrite)
            self.WriteBit(bit)
        
        self.m_lastWriteBits = bitsToWrite

    def PopContent(self, getAll: bool = False) -> bytearray:
        self.m_logger.debug(f"Popping content. leftToWriteBits = {self.m_leftToWriteBits}. Buffer content = {self.m_buffer}")
        
        content = None
        if self.m_leftToWriteBits == self.m_maxBits or getAll:
            content = bytearray(self.m_buffer)
            self.m_buffer.clear()
        else:
            lastIndex = len(self.m_buffer) - 1
            content = self.m_buffer[:lastIndex]
            self.m_buffer = bytearray([self.m_buffer[lastIndex]])
            self.m_logger.debug(f"Updated buffer: {self.m_buffer}. Current byte: {self.m_currentByte:08b}. Byte in buffer: {self.m_buffer[0]:08b}")
        
        self.m_logger.debug(f"Popped content: {content}")
        return content
    
    def MoveBack(self) -> None:
        self.m_logger.debug(f"Moving back. Current state: leftToWriteBits = {self.m_leftToWriteBits}, lastWriteBits = {self.m_lastWriteBits}, currentByte = {self.m_currentByte:08b}")
        self.m_leftToWriteBits = self.m_leftToWriteBits + self.m_lastWriteBits - self.m_maxBits
        self.m_currentByte = self.m_buffer[len(self.m_buffer) - 1]
        self.m_buffer = self.m_buffer[:-1]
        self.m_logger.debug(f"Moved back. Current state: leftToWriteBits = {self.m_leftToWriteBits}, currentByte = {self.m_currentByte:08b}")
        self.DeleteBitsFromEnd(self.m_leftToWriteBits)
        self.m_logger.debug(f"Deleted {self.m_leftToWriteBits} bits. currentByte = {self.m_currentByte:08b}")

    def DeleteBitsFromEnd(self, count: int) -> None:
        self.m_currentByte &= (255 << count)