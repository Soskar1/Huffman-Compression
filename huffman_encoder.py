from typing import Dict, List, Tuple

import binary_tree, byte_analyzer, byte_reader, byte_writer
import argparse, io, logging, sys, time

class HuffmanEncoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, processBits: int, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024, debug: bool = False):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath
        self.m_outFile: io.BufferedWriter = None

        self.m_processBits: int = processBits
        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength

        self.m_bytePopularity: Dict[Tuple[int, str], int] = {}
        self.m_huffmanTreeRootNode: binary_tree.Node = None
        self.m_huffmanCode: Dict[str, str] = {}
        self.m_huffmanHeaderDebug: str = ""

        self.m_debug: bool = debug

        self.m_paddingZeros: int = 0
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.AnalyzeSourceFile()

        if self.m_debug:
            self.m_logger.debug("Byte Popularity Dict content")
            for byte in self.m_bytePopularity.keys():
                self.m_logger.debug(f"{byte[0]:0{self.m_processBits}b} \"{byte[1]}\" | {self.m_bytePopularity[byte]}")
        
        self.ConstructHuffmanTree()

        self.m_logger.info("Constructing Huffman Code...")
        self.ConstructHuffmanCode(self.m_huffmanTreeRootNode)

        self.m_logger.info("Binary | Huffman Code")
        for byte in sorted(self.m_huffmanCode.keys()):
            code = self.m_huffmanCode[byte]
            self.m_logger.info(f"{byte} | {code}")
        
        startTime: float = time.time()
        self.Encode()
        endTime: float = time.time()
        self.m_logger.info(f"Encoder ended his job! Encoding time: {endTime - startTime}s")

    def AnalyzeSourceFile(self) -> None:
        self.m_logger.info(f"Analyzing {self.m_srcFilePath}...")
        self.m_bytePopularity = byte_analyzer.ByteAnalyzer(self.m_srcFilePath, self.m_processBits, debug=self.m_debug).Analyze()

    def ConstructHuffmanTree(self) -> None:
        self.m_logger.info("Constructing Huffman Tree...")

        leafs: List[binary_tree.Node] = []

        for item in self.m_bytePopularity.items():
            byte, count = item[0], item[1]
            node: binary_tree.Node = binary_tree.Node(byte, count)

            leafs.append(node)

        while len(leafs) > 1:
            leafs = sorted(leafs, key = lambda leaf: leaf.m_count)

            left: binary_tree.Node = leafs.pop(0)
            right: binary_tree.Node = leafs.pop(0)

            newByte: int = left.m_byte + right.m_byte
            newCount: int = left.m_count + right.m_count

            newNode: binary_tree.Node = binary_tree.Node(newByte, newCount)
            newNode.AddLeft(left)
            newNode.AddRight(right)

            leafs.append(newNode)

        self.m_huffmanTreeRootNode = leafs.pop(0)

    def ConstructHuffmanCode(self, node: binary_tree.Node, currentCode: str = "") -> None:
        left, right = node.m_left, node.m_right
    
        if left != None:
            self.ConstructHuffmanCode(left, currentCode + '0')

        if right != None:
            self.ConstructHuffmanCode(right, currentCode + '1')

        if node.IsLeaf():
            self.m_huffmanCode[node.m_byte[1]] = currentCode

    def Encode(self) -> None:
        self.m_outFile: io.BufferedWriter = open(self.m_outFilePath, "wb")
        byteWriter: byte_writer.ByteWriter = byte_writer.ByteWriter(debug=self.m_debug)

        ################ FIRST BYTE INFO
        byteWriter.WriteBitsFromByte(self.m_processBits - 2, 4)
        # Leaving space for amount of zero's at the end of file. Max value = 8
        for _ in range(4):
            byteWriter.WriteBit(0)
        ################

        self.m_logger.info(f"Writing huffman header...")
        self.EncodeHuffmanHeader(self.m_huffmanTreeRootNode, byteWriter)
        self.m_logger.info(f"Header: {self.m_huffmanHeaderDebug}")
        
        self.EncodeSourceFile(byteWriter)
        self.m_outFile.close()

        # Find byte with padding zeros
        for byte in self.m_bytePopularity.keys():
            byteInt: int = int(byte[1], 2)
            if byte[0] != byteInt:
                if self.m_debug:
                    self.m_logger.debug(f"Found byte with padding zeros: {byte[1]}. True byte value: {byte[0]:0{self.m_processBits}b}")

                while byte[0] != byteInt:
                    byteInt >>= 1
                    self.m_paddingZeros += 1
                break

        # Need to add info about zero's at the end of file
        if self.m_paddingZeros > 0:
            if self.m_debug:
                self.m_logger.debug(f"Byte writer has {self.m_paddingZeros} padding zeros")
            
            with open(self.m_outFilePath, "r+b") as outFile:
                firstByte: int = int.from_bytes(outFile.read(1), byteorder="big")
                
                if self.m_debug:
                    self.m_logger.debug(f"First byte: {firstByte:08b}")
                
                firstByte |= self.m_paddingZeros
                
                if self.m_debug:
                    self.m_logger.debug(f"Updated to: {firstByte:08b}")
                
                outFile.seek(0)
                outFile.write(bytearray([firstByte]))

    def EncodeHuffmanHeader(self, node: binary_tree.Node, byteWriter: byte_writer.ByteWriter) -> None:
        if not node.IsLeaf() and node.m_parent != None:
            self.m_huffmanHeaderDebug += '0'
            byteWriter.WriteBit(0)
            
            if self.m_debug:
                self.m_logger.debug(f"Appended 0 to header. Current header = {self.m_huffmanHeaderDebug}")
        
        if node.m_left != None:
            self.EncodeHuffmanHeader(node.m_left, byteWriter)
            
        if node.m_right != None:
            self.EncodeHuffmanHeader(node.m_right, byteWriter)
            
        if node.IsLeaf():
            byteWriter.WriteBit(1)

            if self.m_debug:
                 self.m_logger.debug(f"Appended 1 to header. Current header = {self.m_huffmanHeaderDebug}")
            
            byteToWrite: int = int(node.m_byte[1], 2)
            byteWriter.WriteBitsFromByte(byteToWrite, self.m_processBits)
            self.m_huffmanHeaderDebug += node.m_byte[1]
        
        if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
            if self.m_debug:
                self.m_logger.debug(f"ByteWriter buffer filled while trying to write huffman header! Writing content to {self.m_outFilePath}")
            
            content = byteWriter.PopContent()
            self.m_outFile.write(content)

    def EncodeSourceFile(self, byteWriter: byte_writer.ByteWriter) -> None:
        self.m_logger.info(f"Encoding {self.m_srcFilePath}")

        byteReader: byte_reader.ByteReader = byte_reader.ByteReader()
        
        with open(self.m_srcFilePath, "rb") as src:
            def UpdateBuffer() -> bool:
                buffer: bytes = src.read(self.m_srcMaxBufferLength)

                if buffer == b'':
                    return False

                byteReader.SetBuffer(buffer)
                return True
            
            UpdateBuffer()
            while byteReader.CanRead() or UpdateBuffer():
                byte: str = ""
                for _ in range(self.m_processBits):
                    result: int = byteReader.ReadBit()

                    if result == -1:
                        if UpdateBuffer():
                            result = byteReader.ReadBit()
                        else:
                            break

                    byte += str(result)
                
                code: str = self.m_huffmanCode[byte.ljust(self.m_processBits, '0')]

                if self.m_debug:
                    self.m_logger.debug(f'Read {byte}. It\'s code: {code}')

                for bit in code:
                    byteWriter.WriteBit(int(bit))

                if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
                    if self.m_debug:
                        self.m_logger.debug(f"ByteWriter buffer filled while encoding {self.m_srcFilePath}! Writing content to {self.m_outFilePath}")
                    
                    content = byteWriter.PopContent()
                    self.m_outFile.write(content)

        if byteWriter.m_leftToWriteBits != byteWriter.m_maxBits:
            self.m_paddingZeros = byteWriter.m_leftToWriteBits
            byteWriter.UpdateBuffer()

        content = byteWriter.PopContent(getAll=True)
        self.m_outFile.write(content)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("-p", "--processBits", dest="processBits", type = int, default = 8, help = "How much bits to process. By default 8 (1 byte)")
    parser.add_argument("-l", "--logLevel", dest="logLevel", type = int, default = 2, help = "To configure logging messages. 1 - DEBUG, 2 - INFO, 3 - WARNING, 4 - ERROR, 5 - CRITICAL")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    logLevel: int = args.logLevel
    processBits: int = args.processBits
    
    if logLevel <= 0 or logLevel > 5:
        raise Exception("Bad logLevel")
    
    if processBits <= 1 or processBits > 16:
        raise Exception("Bad processBits")
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/encoder.log", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
    encoder: HuffmanEncoder = HuffmanEncoder(srcFile, outFile, processBits, debug = logLevel == 1)
    encoder.Run()

if __name__ == "__main__":
    main()