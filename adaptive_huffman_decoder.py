import argparse, logging, sys, time

import binary_tree, byte_reader

class AdaptiveHuffmanDecoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024, debug: bool = False):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength

        self.m_debug: bool = debug
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))
    
    def Run(self) -> None:
        self.m_logger.info("Decoding...")
        
        startTime: float = time.time()
        self.__Decode()
        endTime: float = time.time()
        
        self.m_logger.info(f"Done. Decoding time: {endTime - startTime}s")

    def __Decode(self) -> None:
        byteReader: byte_reader.ByteReader = byte_reader.ByteReader(debug=self.m_debug)
        outBuffer: bytearray = bytearray()
        with open(self.m_outFilePath, "wb") as outFile:
            with open(self.m_srcFilePath, "rb") as srcFile:
                def UpdateBuffer() -> bool:
                    buffer: bytes = srcFile.read(self.m_srcMaxBufferLength)
                    
                    if buffer == b'':
                        return False
                    
                    byteReader.SetBuffer(buffer)
                    return True
            
                UpdateBuffer()
                            
                # TODO: get tree reconstruction interval value from the first byte
                tree: binary_tree.AdaptiveHuffmanTree = binary_tree.AdaptiveHuffmanTree()
                
                # Getting first character
                byte: int = byteReader.ReadByte()
                outBuffer.append(byte)
                tree.AddSymbol(byte)
                currentCode: str = ""
                
                while byteReader.CanRead() or UpdateBuffer():
                    result: int = byteReader.ReadBit()

                    if result == -1:
                        continue
                    
                    currentCode += str(result)
                    symbol: int = tree.GetSymbol(currentCode)
                    
                    if self.m_debug:
                        self.m_logger.debug(f"Current code: {currentCode}")
                    
                    if symbol == tree.m_nytValue:
                        # NYT node. Read byte, decode and add to the tree
                        result: int = byteReader.ReadByte()
                        
                        if result == -1:
                            if UpdateBuffer():
                                result = byteReader.ReadByte()
                            else:
                                assert False, "End of file"
                                
                        if self.m_debug:
                            self.m_logger.debug(f"Found NYT code {currentCode}. Decoded '{chr(result)}' ({result:08b})")
                        
                        outBuffer.append(result)
                        tree.AddSymbol(result)
                        currentCode = ""
                    elif symbol >= 0:
                        # Decode symbol. Add to the tree
                        if self.m_debug:
                            self.m_logger.debug(f"Decoded '{chr(symbol)}' ({symbol:08b})")
                        
                        outBuffer.append(symbol)
                        tree.AddSymbol(symbol)
                        currentCode = ""
                    
                    if len(outBuffer) > self.m_outMaxBufferLength:
                        if self.m_debug:
                            self.m_logger.debug(f"Out buffer overflow. Writing content to the {self.m_outFilePath}")
                        
                        outFile.write(outBuffer)
                        outBuffer.clear()
            
            if len(outBuffer) > 0:
                outFile.write(outBuffer)
                outBuffer.clear()
                    
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("-l", "--logLevel", dest="logLevel", type = int, default = 2, help = "To configure logging messages. 1 - DEBUG, 2 - INFO, 3 - WARNING, 4 - ERROR, 5 - CRITICAL")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    logLevel: int = args.logLevel
    
    if logLevel <= 0 or logLevel > 5:
        raise Exception("Bad logLevel")
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/adaptive_decoder.log", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
    encoder: AdaptiveHuffmanDecoder = AdaptiveHuffmanDecoder(srcFile, outFile, debug = logLevel == 1)
    encoder.Run()

if __name__ == "__main__":
    main()