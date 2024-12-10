from typing import Dict, List

import binary_tree, byte_analyzer, byte_writer, file_compression_config
import argparse, io, logging, sys, time

class HuffmanEncoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, processBits: int, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath
        self.m_outFile: io.BufferedWriter = None

        self.m_processBits: int = processBits
        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength

        self.m_bytePopularity: Dict[str, int] = {}
        self.m_huffmanTreeRootNode: binary_tree.Node = None
        self.m_huffmanCode: Dict[str, str] = {}
        self.m_huffmanHeader: str = ""
        self.m_endOfFile: str = file_compression_config.ENF_OF_FILE
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.AnalyzeSourceFile()
        
        self.m_bytePopularity[self.m_endOfFile] = 1
        self.ConstructHuffmanTree()

        self.m_logger.info("Constructing Huffman Code...")
        self.ConstructHuffmanCode(self.m_huffmanTreeRootNode)

        self.m_logger.info("Character | Huffman Code | Popularity")
        for byte in sorted(self.m_huffmanCode.keys()):
            code = self.m_huffmanCode[byte]
            self.m_logger.info(f"{byte} | {code} | {self.m_bytePopularity[byte]}")
        
        # startTime: float = time.time()
        self.Encode()
        # endTime: float = time.time()
        # self.m_logger.info(f"Encoder ended his job! Encoding time: {endTime - startTime}s")

    def AnalyzeSourceFile(self) -> None:
        self.m_logger.info(f"Analyzing {self.m_srcFilePath}...")
        self.m_bytePopularity = byte_analyzer.ByteAnalyzer(self.m_srcFilePath, self.m_processBits).Analyze()

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

            newByte: str = left.m_bytes + right.m_bytes
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
            self.m_huffmanCode[node.m_bytes] = currentCode

    def Encode(self) -> None:
        self.m_outFile: io.BufferedWriter = open(self.m_outFilePath, "wb")
        byteWriter: byte_writer.ByteWriter = byte_writer.ByteWriter()

        byteWriter.WriteBitsFromByte(self.m_processBits - 2, 4) 
        
        uniqueCharacters: int = len(self.m_huffmanCode.keys()) - 2
        self.m_logger.info(f"Encoder encountered {uniqueCharacters + 1} unique characters.")
        
        byteWriter.WriteBitsFromByte(uniqueCharacters, self.m_processBits)

        self.m_logger.info(f"Writing huffman header...")
        self.EncodeHuffmanHeader(self.m_huffmanTreeRootNode, byteWriter)
        self.m_logger.info(f"Header: {self.m_huffmanHeader}")
        # self.EncodeSourceFile(byteWriter)
        
        if len(byteWriter.m_buffer) > 0:
            self.m_logger.info(f"Writing to file {byteWriter.m_buffer}")
            if byteWriter.m_leftToWriteBits != 8:
                byteWriter.UpdateBuffer()
            content = byteWriter.PopContent()
            self.m_outFile.write(content)
        
        self.m_outFile.close()

    def EncodeHuffmanHeader(self, node: binary_tree.Node, byteWriter: byte_writer.ByteWriter) -> None:
        if not node.IsLeaf() and node.m_parent != None:
            self.m_huffmanHeader += '0'
            byteWriter.WriteBit(0)
            self.m_logger.debug(f"Appended 0 to header. Current header = {self.m_huffmanHeader}")
        
        if node.m_left != None:
            self.EncodeHuffmanHeader(node.m_left, byteWriter)
            
        if node.m_right != None:
            self.EncodeHuffmanHeader(node.m_right, byteWriter)
            
        if node.IsLeaf():
            self.m_huffmanHeader += '1'
            byteWriter.WriteBit(1)
            self.m_logger.debug(f"Appended 1 to header. Current header = {self.m_huffmanHeader}")
            
            # Insert byte size for decoder
            if self.m_processBits > 8:
                if len(node.m_bytes) == 1:
                    byteWriter.WriteBit(0) # size 1
                else:
                    byteWriter.WriteBit(1) # size 2 or more

            for byte in node.m_bytes:
                self.m_huffmanHeader += byte
                byteWriter.WriteByte(ord(byte))
                
                binaryList = [format(ord(char), '08b') for char in byte]
                self.m_logger.debug(f'Appended "{byte}" ({binaryList}) to header. Current header = {self.m_huffmanHeader}')
        
        if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
            self.m_logger.debug(f"ByteWriter buffer filled while trying to write huffman header! Writing content to {self.m_outFilePath}")
            content = byteWriter.PopContent()
            self.m_outFile.write(content)

    def EncodeSourceFile(self, byteWriter: byte_writer.ByteWriter) -> None:
        self.m_logger.info(f"Encoding {self.m_srcFilePath}")
        with open(self.m_srcFilePath, "rb") as src:
            while True:
                readBuffer: bytes = src.read(self.m_srcMaxBufferLength)

                if readBuffer == b'':
                    break

                for byte in readBuffer:
                    char: chr = chr(byte)
                    code = self.m_huffmanCode[char]
                    self.m_logger.debug(f'Read "{char}". It\'s code: {code}')
                    for bit in code:
                        byteWriter.WriteBit(int(bit))

                    if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
                        self.m_logger.debug(f"ByteWriter buffer filled while encoding {self.m_srcFilePath}! Writing content to {self.m_outFilePath}")
                        content = byteWriter.PopContent()
                        self.m_outFile.write(content)

        self.m_logger.debug(f"Adding {self.m_endOfFile}")
        endOfFileCode = self.m_huffmanCode[self.m_endOfFile]
        for bit in endOfFileCode:
            byteWriter.WriteBit(int(bit))

        if byteWriter.m_leftToWriteBits != byteWriter.m_maxBits:
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
        
    encoder: HuffmanEncoder = HuffmanEncoder(srcFile, outFile, processBits)
    encoder.Run()

if __name__ == "__main__":
    main()