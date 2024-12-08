from typing import Dict, List

import binary_tree, byte_analyzer, byte_writer
import argparse, io, logging, sys

class HuffmanEncoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength

        self.m_bytePopularity: Dict[chr, int] = {}
        self.m_huffmanTreeRootNode: binary_tree.Node = None
        self.m_huffmanCode: Dict[str, str] = {}
        self.m_huffmanHeader: str = ""
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.AnalyzeSourceFile()
        self.ConstructHuffmanTree()

        self.m_logger.info("Constructing Huffman Code...")
        self.ConstructHuffmanCode(self.m_huffmanTreeRootNode)

        self.m_logger.info("Character | Huffman Code | Popularity | ASCII Code")
        for byte in sorted(self.m_huffmanCode.keys()):
            code = self.m_huffmanCode[byte]
            self.m_logger.info(f"{byte} | {code} | {self.m_bytePopularity[byte]} | {ord(byte)}")

        self.m_logger.info("Constructing Huffman Header...")
        self.ConstructHuffmanHeader(self.m_huffmanTreeRootNode)
        self.m_logger.info(f"Huffman Header: {self.m_huffmanHeader}")

        self.Encode()

    def AnalyzeSourceFile(self) -> None:
        self.m_logger.info(f"Analyzing {self.m_srcFilePath}...")
        self.m_bytePopularity = byte_analyzer.ByteAnalyzer(self.m_srcFilePath).Analyze()

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

    def ConstructHuffmanHeader(self, node: binary_tree.Node) -> None:
        if not node.IsLeaf() and node.m_parent != None:
            self.m_huffmanHeader += '0'
            self.m_logger.debug(f"Appended 0 to header. Current header = {self.m_huffmanHeader}")
        
        if node.m_left != None:
            self.ConstructHuffmanHeader(node.m_left)
            
        if node.m_right != None:
            self.ConstructHuffmanHeader(node.m_right)
            
        if node.IsLeaf():
            self.m_huffmanHeader += '1'
            self.m_logger.debug(f"Appended 1 to header. Current header = {self.m_huffmanHeader}")
            
            for byte in node.m_bytes:
                self.m_huffmanHeader += byte
                self.m_logger.debug(f'Appended "{byte}" ({ord(byte):08b}) to header. Current header = {self.m_huffmanHeader}')

    def Encode(self) -> None:
        outFile: io.BufferedWriter = open(self.m_outFilePath, "wb")

        uniqueCharacters: int = len(self.m_huffmanCode.keys()) - 1
        self.m_logger.info(f"Encoder encountered {uniqueCharacters + 1} unique characters.")

        byteWriter: byte_writer.ByteWriter = byte_writer.ByteWriter()
        byteWriter.WriteByte(uniqueCharacters)

        self.m_logger.info(f"Writing huffman header...")
        index: int = 0

        while index < len(self.m_huffmanHeader):
            if self.m_huffmanHeader[index] == '0':
                byteWriter.WriteBit(0)
                index += 1
            elif self.m_huffmanHeader[index] == '1':
                byteWriter.WriteBit(1)
                byteWriter.WriteByte(ord(self.m_huffmanHeader[index + 1]))
                index += 2

            if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
                self.m_logger.debug(f"ByteWriter buffer filled while trying to write huffman header! Writing content to {self.m_outFilePath}")
                outFile.write(byteWriter.m_buffer)

        self.m_logger.info(f"Encoding {self.m_srcFilePath}")
        with open(self.m_srcFilePath, "r") as src:
            while True:
                readBuffer: str = src.read(self.m_srcMaxBufferLength)

                if readBuffer == "":
                    break

                for byte in readBuffer:
                    code = self.m_huffmanCode[byte]
                    self.m_logger.debug(f"Read {byte}. It's code: {code}")
                    for bit in code:
                        byteWriter.WriteBit(int(bit))

                    if len(byteWriter.m_buffer) >= self.m_outMaxBufferLength:
                        self.m_logger.debug(f"ByteWriter buffer filled while encoding {self.m_srcFilePath}! Writing content to {self.m_outFilePath}")
                        outFile.write(byteWriter.m_buffer)

        if byteWriter.m_leftToWriteBits != byteWriter.m_maxBits:
            byteWriter.UpdateBuffer()

        outFile.write(byteWriter.m_buffer)
        outFile.close()
        self.m_logger.info("Done")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("--logLevel", type = int, default = 2, help = "To configure logging messages. 1 - DEBUG, 2 - INFO, 3 - WARNING, 4 - ERROR, 5 - CRITICAL")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    logLevel: int = args.logLevel
    
    if logLevel <= 0 or logLevel > 5:
        raise Exception("Bad logLevel")
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/encoder.txt", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
    encoder: HuffmanEncoder = HuffmanEncoder(srcFile, outFile)
    encoder.Run()

if __name__ == "__main__":
    main()