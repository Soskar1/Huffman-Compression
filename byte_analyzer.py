from typing import Dict

import byte_reader
import io

class ByteAnalyzer(object):
    def __init__(self, fileName: str, processBits: int, bufferSize: int = 1024):
        self.m_fileName: str = fileName
        self.m_bufferSize: int = bufferSize
        self.m_processBits: int = processBits

    def Analyze(self) -> Dict[str, int]:
        bytePopularity: Dict[str, int] = {}
        byteReader: byte_reader.ByteReader = byte_reader.ByteReader()
        
        def UpdateBuffer(srcFile: io.BufferedReader) -> bool:
            buffer: bytes = srcFile.read(self.m_bufferSize)

            if buffer == b'':
                return False

            byteReader.SetBuffer(buffer)
            return True

        with open(self.m_fileName, "rb") as srcFile:
            while byteReader.CanRead() or UpdateBuffer(srcFile):
                byteToAdd: str = ""
                if self.m_processBits % 8 == 0:
                    for _ in range((int)(self.m_processBits / 8)):
                        byte: int = byteReader.ReadByte()
                        byteToAdd += chr(byte)
                elif self.m_processBits / 8 > 0:
                    byte: int = byteReader.ReadByte()
                    # TODO: read other bits
                else:
                    # TODO: read bits
                    pass
                
                if byteToAdd not in bytePopularity:
                    bytePopularity[byteToAdd] = 0
                
                bytePopularity[byteToAdd] += 1
                byteToAdd = ""

        return bytePopularity
