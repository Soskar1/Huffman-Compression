from typing import Dict

import byte_reader
import io

class ByteAnalyzer(object):
    def __init__(self, fileName: str, processBits: int, bufferSize: int = 1024, debug: bool = False):
        self.m_fileName: str = fileName
        self.m_bufferSize: int = bufferSize
        self.m_processBits: int = processBits
        self.m_debug: bool = debug

    def Analyze(self) -> Dict[int, int]:
        bytePopularity: Dict[int, int] = {}
        byteReader: byte_reader.ByteReader = byte_reader.ByteReader(debug=self.m_debug)
        srcFile: io.BufferedReader = open(self.m_fileName, "rb")
        
        def UpdateBuffer() -> bool:
            buffer: bytes = srcFile.read(self.m_bufferSize)

            if buffer == b'':
                return False

            byteReader.SetBuffer(buffer)
            return True

        UpdateBuffer()
        while byteReader.CanRead() or UpdateBuffer():
            byte: int = 0
            for _ in range(self.m_processBits):
                result: int = byteReader.ReadBit()

                if result == -1:
                    if UpdateBuffer():
                        result = byteReader.ReadBit()
                    else:
                        break
                
                byte <<= 1
                byte |= result
            
            if byte not in bytePopularity:
                bytePopularity[byte] = 0

            bytePopularity[byte] += 1

        srcFile.close()
        return bytePopularity
