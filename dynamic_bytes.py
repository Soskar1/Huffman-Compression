from typing import List

class DynamicBytes(object):
    def __init__(self):
        self.m_bytes: bytearray = bytearray([1])
        self.m_notFilledByteIndex: int = 0
        
    def IsByteFilled(self, byte) -> bool:
        return (byte & 0b10000000) > 0
    
    def IsEmpty(self, byte) -> bool:
        return (byte & 0b11111110) == 0
    
    def GetBytes(self) -> List[int]:
        return [byte for byte in self.m_bytes if not self.IsEmpty(byte)]
    
    def Increment(self) -> None:
        self.m_bytes[self.m_notFilledByteIndex] += 1
        
    def Shift(self) -> None:
        byte = self.m_bytes[self.m_notFilledByteIndex]
        
        if self.IsByteFilled(byte):
            self.m_bytes.append(1)
            self.m_notFilledByteIndex += 1
            byte = self.m_bytes[self.m_notFilledByteIndex]
        
        byte = byte << 1
        self.m_bytes[self.m_notFilledByteIndex] = byte
    
    def __str__(self):
        byteStr: str = ""
        bytes: List[int] = self.GetBytes()
        for byte in bytes:
            if not self.IsEmpty(byte):
                byteStr += f"{byte:08b} "
            
        return byteStr
    
if __name__ == '__main__':
    myByteArray: DynamicBytes = DynamicBytes()
    
    myByteArray.Shift()
    myByteArray.Increment()
    myByteArray.Shift()
    myByteArray.Shift()
    myByteArray.Shift()
    myByteArray.Increment()
    myByteArray.Shift()
    myByteArray.Shift()
    myByteArray.Increment()
    myByteArray.Shift()
    myByteArray.Increment()
    myByteArray.Shift()
    
    print(myByteArray)
    