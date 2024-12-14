import argparse, logging, sys, time

import binary_tree, byte_writer

class AdaptiveHuffmanEncoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, treeReconstructionInterval: int = 1, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024, debug: bool = False):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength
        self.m_treeReconstructionInterval: int = treeReconstructionInterval

        self.m_tree: binary_tree.AdaptiveHuffmanTree = binary_tree.AdaptiveHuffmanTree(treeReconstructionInterval)

        self.m_debug: bool = debug
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))
    
    def Run(self) -> None:
        self.m_logger.info("Encoding...")
        
        startTime: float = time.time()
        self.__Encode()
        endTime: float = time.time()
        
        self.m_logger.info(f"Done. Encoding time: {endTime - startTime}s")

    def __Encode(self) -> None:
        byteWriter: byte_writer.ByteWriter = byte_writer.ByteWriter(self.m_debug)
        paddingZeros: int = 0

        # Leaving space for padding zeros amount at the end of file. Max value 7 (0b111)
        for _ in range(3):
            byteWriter.WriteBit(0)

        with open(self.m_outFilePath, "wb") as outFile:
            with open(self.m_srcFilePath, "rb") as srcFile:
                while (buffer := srcFile.read(self.m_srcMaxBufferLength)) != b'':
                    for byte in buffer:
                        code: str = self.m_tree.GetHuffmanCode(byte)

                        if self.m_debug:
                            self.m_logger.debug(f"Got '{chr(byte)}' ({byte:08b}). Huffman code: {code}")

                        self.m_tree.AddSymbol(byte)

                        byteWriter.WriteBitsFromByte(int(code, 2), len(code))

                        if len(byteWriter.m_buffer) > self.m_outMaxBufferLength:
                            content = byteWriter.PopContent()
                            outFile.write(content)

            if byteWriter.m_leftToWriteBits < 8:
                paddingZeros = byteWriter.m_leftToWriteBits
                byteWriter.AppendByteToBuffer()
            
            if len(byteWriter.m_buffer) > 0:
                content = byteWriter.PopContent(getAll=True)
                outFile.write(content)

        if paddingZeros > 0:
            if self.m_debug:
                self.m_logger.debug(f"Padding zeros = {paddingZeros}")

            with open(self.m_outFilePath, "r+b") as outFile:
                firstByte: int = int.from_bytes(outFile.read(1), byteorder="big")
                
                if self.m_debug:
                    self.m_logger.debug(f"First byte: {firstByte:08b}")
                
                firstByte |= paddingZeros << 5
                
                if self.m_debug:
                    self.m_logger.debug(f"Updated to: {firstByte:08b}")
                
                outFile.seek(0)
                outFile.write(bytearray([firstByte]))
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("-l", "--logLevel", dest="logLevel", type = int, default = 2, help = "To configure logging messages. 1 - DEBUG, 2 - INFO, 3 - WARNING, 4 - ERROR, 5 - CRITICAL")
    parser.add_argument("-r", "--reconstructionInterval", dest="reconstructionInterval", type = int, default = 1, help = "Huffman tree reconstruction interval")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    reconstructionInterval: int = args.reconstructionInterval
    logLevel: int = args.logLevel

    if reconstructionInterval <= 0:
        raise Exception("Bad reconstructionInterval")
    
    if logLevel <= 0 or logLevel > 5:
        raise Exception("Bad logLevel")
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/adaptive_encoder.log", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
    encoder: AdaptiveHuffmanEncoder = AdaptiveHuffmanEncoder(srcFile, outFile, treeReconstructionInterval = reconstructionInterval, debug = logLevel == 1)
    encoder.Run()

if __name__ == "__main__":
    main()