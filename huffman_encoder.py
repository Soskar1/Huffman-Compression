from typing import Dict, List

import binary_tree, byte_analyzer, dynamic_bytes, huffman_code_writer, huffman_header
import argparse, io, logging, sys

class HuffmanEncoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength

        self.m_bytePopularity: Dict[chr, int] = {}
        self.m_huffmanTreeRootNode: binary_tree.Node = None
        self.m_huffmanCode: Dict[str, dynamic_bytes.DynamicBytes] = {}
        
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.AnalyzeSourceFile()
        self.ConstructHuffmanTree()

        self.m_logger.info("Constructing Huffman Code...")
        self.ConstructHuffmanCode()

        self.m_logger.info("Character | Huffman Code | Popularity | ASCII Code")
        for byte in sorted(self.m_huffmanCode.keys()):
            code = self.m_huffmanCode[byte]
            self.m_logger.info(f"{byte} | {code} | {self.m_bytePopularity[byte]} | {ord(byte)}")

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

    def ConstructHuffmanCode(self, node: binary_tree.Node, currentCode: dynamic_bytes.DynamicBytes = dynamic_bytes.DynamicBytes()) -> None:
        left, right = node.m_left, node.m_right
    
        if left != None:
            newCode = currentCode.DeepCopy()
            newCode.Shift()
            self.ConstructHuffmanCode(left, newCode)

        if right != None:
            newCode = currentCode.DeepCopy()
            newCode.Shift()
            newCode.Increment()
            self.ConstructHuffmanCode(right, newCode)

        if node.IsLeaf(): 
            self.m_huffmanCode[node.m_bytes] = currentCode

    def Encode(self) -> None:
        self.m_logger.info("Constructing Huffman Header...")
        huffmanHeader: huffman_header.HuffmanHeader = huffman_header.HuffmanHeader(self.m_huffmanTreeRootNode)
        self.m_logger.info(f"Huffman Header: {huffmanHeader.m_debugHeader}")

        codeWriter: huffman_code_writer.HuffmanCodeWriter = huffman_code_writer.HuffmanCodeWriter(huffmanHeader)
        outFile: io.BufferedWriter = open(self.m_outFilePath, "wb")

        self.m_logger.info("Encoding...")
        with open(self.m_srcFilePath, "rb") as src:
            uniqueCharacters: chr = chr(len(self.m_huffmanCode.keys()) - 1)
            self.m_logger.info(f"Encoder encountered {ord(uniqueCharacters) + 1} unique characters. Writing to {self.m_outFilePath}")

            outFile.write(uniqueCharacters.encode('latin1'))

            while True:
                readBuffer = src.read(self.m_srcMaxBufferLength)

                if readBuffer == b'':
                    break

                for byte in readBuffer:
                    codeWriter.WriteCode(self.m_huffmanCode[chr(byte)])

                    if len(codeWriter.m_buffer) >= self.m_outMaxBufferLength:
                        self.m_logger.debug(f"Write buffer is full! Adding content to {self.m_outFilePath}")

                        outFile.write(codeWriter.m_buffer)
                        codeWriter.m_buffer.clear()

        codeWriter.End()

        if len(codeWriter.m_buffer) > 0:
            outFile.write(codeWriter.m_buffer)

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