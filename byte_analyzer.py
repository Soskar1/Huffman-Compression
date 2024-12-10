from typing import Dict

import byte_reader
import io

class ByteAnalyzer(object):
    def __init__(self, fileName: str, processBits: int, bufferSize: int = 1024, debug: bool = False):
        self.m_fileName: str = fileName
        self.m_bufferSize: int = bufferSize
        self.m_processBits: int = processBits
        self.m_debug: bool = debug

    def Analyze(self) -> Dict[str, int]:
        bytePopularity: Dict[str, int] = {}
        byteReader: byte_reader.ByteReader = byte_reader.ByteReader(debug=self.m_debug)
        srcFile: io.BufferedReader = open(self.m_fileName, "rb")
        
        def UpdateBuffer() -> bool:
            buffer: bytes = srcFile.read(self.m_bufferSize)

            if buffer == b'':
                return False

            byteReader.SetBuffer(buffer)
            return True

        def ConstructByte(bitsToProcess: int) -> chr:
            byte: chr = 0b0
            readBits = 0
            for _ in range(bitsToProcess):
                result: int = byteReader.ReadBit()
                
                if result == -1:
                    if UpdateBuffer():
                        result = byteReader.ReadBit()
                    else:
                        if readBits > 0:
                            return byte
                        else:
                            return -1
                
                byte <<= 1
                byte |= result
                readBits += 1
            
            return byte

        def ReadByte() -> int:
            result: int = byteReader.ReadByte()
                    
            if result == -1:
                if UpdateBuffer():
                    result = byteReader.ReadByte()
            
            return result                    

        UpdateBuffer()
        while byteReader.CanRead() or UpdateBuffer():
            byteToAdd: str = ""
            if self.m_processBits % 8 == 0:
                for _ in range((int)(self.m_processBits / 8)):
                    result: int = ReadByte()
                    if result == -1:
                        break
                    
                    byteToAdd += chr(result)
            elif (int)(self.m_processBits / 8) > 0:
                numberOfBytes: int = (int)(self.m_processBits / 8)
                bitsToProcess: int = self.m_processBits - numberOfBytes * 8
                
                for _ in range(numberOfBytes):
                    result: int = ReadByte()
                    if result == -1:
                        bitsToProcess = byteReader.m_leftToReadBits
                        break
                    
                    byteToAdd += chr(result)
                
                if bitsToProcess > 0:
                    result: int = ConstructByte(bitsToProcess)
                    if result != -1:
                        byteToAdd += chr(result)
            else:
                result: int = ConstructByte(self.m_processBits)
                if result != -1:
                    byteToAdd = chr(result)
            
            if len(byteToAdd) > 0:
                if byteToAdd not in bytePopularity:
                    bytePopularity[byteToAdd] = 0

                bytePopularity[byteToAdd] += 1
            byteToAdd = ""

        srcFile.close()
        return bytePopularity
