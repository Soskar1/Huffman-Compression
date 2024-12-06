import logging

from enum import Enum

class ByteReaderErrorCodes(Enum):
    END_OF_BUFFER = -1

class ByteReader(object):
    def __init__(self, buffer: bytes = bytes([0])):
        self.m_buffer: bytes = buffer
        self.m_currentByte: bytes = buffer[0]
        self.m_maxBits: int = 8
        self.m_leftToReadBits: int = 8
        self.m_currentByteIndex: int = 0
        self.m_logger: logging.Logger = logging.getLogger(__name__)

        self.m_useMemory: bool = False
        self.m_memory: int = 0

    def DoesNextByteExist(self) -> bool:
        return self.m_currentByteIndex + 1 <= (len(self.m_buffer) - 1)

    def Next(self) -> bool:
        if self.DoesNextByteExist():
            self.m_currentByteIndex += 1
            self.m_currentByte = self.m_buffer[self.m_currentByteIndex]
            return True
        
        return False

    def ReadBit(self) -> bool | ByteReaderErrorCodes:
        if self.m_leftToReadBits == 0:
            if not self.Next():
                self.m_logger.debug(f"ReadBit {ByteReaderErrorCodes.END_OF_BUFFER}")
                return ByteReaderErrorCodes.END_OF_BUFFER.value
            else:
                self.m_leftToReadBits = self.m_maxBits
        
        self.m_leftToReadBits -= 1

        if self.m_leftToReadBits == 8:
            return True if self.m_currentByte & 0b10000000 == 0b10000000 else False
        if self.m_leftToReadBits == 7:
            return True if self.m_currentByte & 0b1000000 == 0b1000000 else False
        if self.m_leftToReadBits == 6:
            return True if self.m_currentByte & 0b100000 == 0b100000 else False
        if self.m_leftToReadBits == 5:
            return True if self.m_currentByte & 0b10000 == 0b10000 else False
        if self.m_leftToReadBits == 4:
            return True if self.m_currentByte & 0b1000 == 0b1000 else False
        if self.m_leftToReadBits == 3:
            return True if self.m_currentByte & 0b100 == 0b100 else False
        if self.m_leftToReadBits == 2:
            return True if self.m_currentByte & 0b10 == 0b10 else False
        if self.m_leftToReadBits == 1:
            return True if self.m_currentByte & 0b1 == 0b1 else False

    def ReadByte(self) -> int | ByteReaderErrorCodes:
        if self.m_leftToReadBits == 0:
            if not self.Next():
                self.m_logger.debug(f"ReadByte {ByteReaderErrorCodes.END_OF_BUFFER}")
                return ByteReaderErrorCodes.END_OF_BUFFER.value
            else:
                return ord(self.m_currentByte)
        
        # Left to read bits in range [1, 7]
        if not self.DoesNextByteExist():
            self.m_memory = ord(self.m_currentByte)
            self.m_useMemory = True
            self.m_logger.debug(f"The next byte must be read, but reached {ByteReaderErrorCodes.END_OF_BUFFER}. Saving {self.m_currentByte} to memory")
            return ByteReaderErrorCodes.END_OF_BUFFER.value
        
        leftBytePiece: int = 0
        if not self.m_useMemory:
            leftBytePiece = self.ShiftByte(self.m_currentByte)
            self.Next()
        else:
            self.m_logger.debug(f"ByteReader has memory ({self.m_memory}). Using it to construct byte")
            leftBytePiece: int = self.ShiftByte(self.m_memory)

            self.m_memory = 0
            self.m_useMemory = False
        
        rightBytePiece: int = ord(self.m_currentByte) >> self.m_leftToReadBits
        return leftBytePiece | rightBytePiece

    def ShiftByte(self, byteToShift: bytes) -> int:
        byte: int = ord(byteToShift)
        shiftTimes: int = self.m_maxBits - self.m_leftToReadBits

        if shiftTimes == 7:
            return (byte & 0b1) << shiftTimes
        if shiftTimes == 6:
            return (byte & 0b11) << shiftTimes
        if shiftTimes == 5:
            return (byte & 0b111) << shiftTimes
        if shiftTimes == 4:
            return (byte & 0b1111) << shiftTimes
        if shiftTimes == 3:
            return (byte & 0b11111) << shiftTimes
        if shiftTimes == 2:
            return (byte & 0b111111) << shiftTimes
        if shiftTimes == 1:
            return (byte & 0b1111111) << shiftTimes
    
    def SetBuffer(self, buffer: bytes) -> None:
        self.m_buffer = buffer
        self.m_currentByteIndex = 0
        self.m_currentByte = buffer[0]