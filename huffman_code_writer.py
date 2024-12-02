from dynamic_bytes import DynamicBytes

class HuffmanCodeWriter(object):
    def __init__(self, debug: bool = False):
        self.m_buffer: bytearray = bytearray()
        self.m_notFilledByte: chr = 0b0
        self.m_freeBits: int = 8
        self.m_maxBits: int = 8
        self.m_debug: bool = debug
        
    def HasMostLeftBit(self, code: chr) -> bool:
        return code & 0b10000000 == 0b10000000
    
    def HasMostRightBit(self, code: chr) -> bool:
        return code & 0b1 == 0b1
    
    def WriteCode(self, code: DynamicBytes) -> None:
        code = code.GetBytes()[0] # TODO: Fix it
        length: int = self.m_maxBits

        while not self.HasMostLeftBit(code):
            code <<= 1
            length -= 1
            
        code = (code & 0b01111111) << 1
        length -= 1
        
        if self.m_debug:
            print(f"{code:08b} with length={length}")
        
        self.WriteByte(code, length)
    
    def WriteByte(self, byte: chr, length: int) -> None:
        if length <= self.m_freeBits:
            byte >>= self.m_maxBits - self.m_freeBits
            self.m_notFilledByte |= byte
            self.m_freeBits -= length
            
            if self.m_debug:    
                print(f"Not filled byte: {self.m_notFilledByte:08b}. Left bits: {self.m_freeBits}")
            
            if self.m_freeBits == 0:
                self.AddByteToBuffer()
                self.m_notFilledByte = 0b0
                self.m_freeBits = self.m_maxBits
        else:
            byte >>= self.m_maxBits - length
            
            tmp: chr = 0b0
            tmpLength: int = length - self.m_freeBits
            while length > self.m_freeBits:
                tmp >>= 1
                
                if self.HasMostRightBit(byte):
                    tmp |= 0b10000000
                
                byte >>= 1
                length -= 1
                
            self.m_notFilledByte |= byte
            
            if self.m_debug:
                print(f"Not filled byte: {self.m_notFilledByte:08b}. Left bits: 0")
                print(f"Tmp byte: {tmp:08b}, tmpLength: {tmpLength}")
            
            self.AddByteToBuffer()
            
            self.m_notFilledByte = tmp
            self.m_freeBits = self.m_maxBits - tmpLength
    
    def AddByteToBuffer(self) -> None:
        self.m_buffer.append(self.m_notFilledByte)
    
    def End(self) -> None:
        if self.m_freeBits != self.m_maxBits:
            self.AddByteToBuffer()