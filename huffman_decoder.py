import argparse, logging, os, sys

import binary_tree, byte_reader

class HuffmanDecoder(object):
    def __init__(self, srcFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024):
        self.srcFilePath: str = srcFilePath
        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength
        
        self.m_byteReader: byte_reader.ByteReader = byte_reader.ByteReader()
        self.m_huffmanTreeRootNode: binary_tree.Node = binary_tree.Node()

        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def UpdateReadBuffer(self, src) -> bool:
        buffer: bytes = src.read(self.m_srcMaxBufferLength)

        if buffer == b'':
            return False

        self.m_byteReader.SetBuffer(buffer)
        return True

    def DecodeHuffmanTree(self) -> None:
        self.m_logger.info("Decoding Huffman Tree...")
        huffmanTreeDebug: str = ""
        endOfBufferErrorMessage: str = "Reached end of buffer while decoding Huffman Tree"

        with open(self.srcFilePath, "rb") as src:
            uniqueCharacterCount: int = ord(src.read(1)) + 1
            self.m_logger.info(f"Decoder knows that {self.srcFilePath} have {uniqueCharacterCount} unique characters")

            currentNode: binary_tree.Node = self.m_huffmanTreeRootNode

            self.UpdateReadBuffer(src)
            while uniqueCharacterCount > 0:
                status: int = self.m_byteReader.ReadBit()
                newNode: binary_tree.Node = binary_tree.Node()
                if status == 0:
                    huffmanTreeDebug += '0'

                    if currentNode.m_left == None:
                        currentNode.AddLeft(newNode)
                        currentNode = newNode
                    elif currentNode.m_right == None:
                        currentNode.AddRight(newNode)
                        currentNode = newNode
                elif status == 1: # Construct new Node with next byte value
                    huffmanTreeDebug += '1'
                    result: int = self.m_byteReader.ReadByte()

                    if result == -1: # Reached end of buffer. Update Buffer
                        self.m_logger.debug("ReadByte. Updating buffer")
                        if not self.UpdateReadBuffer(src):
                            self.m_logger.error(endOfBufferErrorMessage)
                            assert False, endOfBufferErrorMessage
                        
                        result: int = self.m_byteReader.ReadByte()

                    # TODO: Add support for more than 1 byte source
                    newNode.m_bytes = chr(result)
                    uniqueCharacterCount -= 1

                    huffmanTreeDebug += newNode.m_bytes

                    if currentNode.m_left == None:
                        currentNode.AddLeft(newNode)
                    elif currentNode.m_right == None:
                        currentNode.AddRight(newNode)
                        while currentNode.m_left != None and currentNode.m_right != None and currentNode.m_parent != None:
                            currentNode.m_bytes = currentNode.m_left.m_bytes + currentNode.m_right.m_bytes
                            currentNode = currentNode.m_parent
                elif status == -1: # Reached end of buffer. Update buffer
                    self.m_logger.debug("ReadBit. Updating buffer")
                    if not self.UpdateReadBuffer(src):
                        self.m_logger.error(endOfBufferErrorMessage)
                        assert False, endOfBufferErrorMessage
        
        self.m_logger.info(f"Decoded Huffman Tree: {huffmanTreeDebug}")

def main():
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
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/decoder.txt", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    decoder: HuffmanDecoder = HuffmanDecoder(srcFile)
    decoder.DecodeHuffmanTree()

    # Create Huffman Code dictionary

    # Decode

if __name__ == "__main__":
    main()