import collections, logging

class ByteWriter(object):
    def __init__(self, useHistory: bool = False, debug: bool = False):
        self.m_buffer: bytearray = bytearray()
        self.m_currentByte: int = 0b0
        self.m_maxBits: int = 8
        self.m_leftToWriteBits: int = 8
        
        self.m_useHistory: bool = useHistory
        self.m_writerHistory: collections.deque = collections.deque([])
        self.m_writeHistoryCapacity: int = 64

        self.m_zeroCount: int = 0

        self.m_debug: bool = debug
        self.m_logger: logging.Logger = logging.getLogger(__name__)

    def UpdateBuffer(self):
        self.m_buffer.append(self.m_currentByte)

        if self.m_debug:
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
        if self.m_debug:
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
        if self.m_debug:
            self.m_logger.debug(f"Trying to write {bitsToWrite} bits from {byte:08b}")
        
        for bitPosition in range(bitsToWrite):
            bit: int = self.GetBitAtPosition(byte, bitPosition, bitsToWrite)
            self.WriteBit(bit)

    def PopContent(self, getAll: bool = False) -> bytearray:
        if self.m_debug:
            self.m_logger.debug(f"Popping content. leftToWriteBits = {self.m_leftToWriteBits}. Buffer content = {self.m_buffer}")
        
        content = None
        if self.m_leftToWriteBits == self.m_maxBits or getAll:
            content = bytearray(self.m_buffer)
            self.m_buffer.clear()
        else:
            lastIndex = len(self.m_buffer) - 1
            content = self.m_buffer[:lastIndex]
            self.m_buffer = bytearray([self.m_buffer[lastIndex]])
            
            if self.m_debug:
                self.m_logger.debug(f"Updated buffer: {self.m_buffer}. Current byte: {self.m_currentByte:08b}. Byte in buffer: {self.m_buffer[0]:08b}")
        
        if self.m_debug:
            self.m_logger.debug(f"Popped content: {content}")
        
        return content

    def Undo(self) -> None:
        if self.m_debug:
            self.m_logger.debug(f"Before undo: zeroCount = {self.m_zeroCount}, buffer = {self.m_buffer}")

        self.m_writerHistory.pop()
        lastState: ByteWriterState = self.m_writerHistory[-1]

        self.m_buffer = lastState.m_buffer
        self.m_zeroCount = lastState.m_zeroCount

        if self.m_debug:
            self.m_logger.debug(f"After undo: zeroCount = {self.m_zeroCount}, buffer = {self.m_buffer}")

    def __AddToHistory(self) -> None:
        writerState: ByteWriterState = ByteWriterState(self)
        self.m_writerHistory.append(writerState)

        if len(self.m_writerHistory) > self.m_writeHistoryCapacity:
            self.m_writerHistory.popleft()

class ByteWriterState(object):
    def __init__(self, writer: ByteWriter):
        self.m_buffer: bytearray = writer.m_buffer.copy()
        self.m_zeroCount: int = writer.m_zeroCount