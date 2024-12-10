from typing import Dict

import binary_tree, byte_reader, file_compression_config
import argparse, io, logging, sys, time

class HuffmanDecoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath
        self.m_srcFile: io.BufferedReader = None

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength
        
        self.m_byteReader: byte_reader.ByteReader = byte_reader.ByteReader()
        self.m_huffmanTreeRootNode: binary_tree.Node = binary_tree.Node()
        self.m_huffmanCode: Dict[str, str] = {}
        
        self.m_endOfFile: str = file_compression_config.ENF_OF_FILE

        self.m_processBits: int = 0

        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.m_srcFile = open(self.m_srcFilePath, "rb")
        self.DecodeHuffmanTree()

        # self.m_logger.info("Constructing Huffman Code...")
        # self.ConstructHuffmanCode(self.m_huffmanTreeRootNode)

        # self.m_logger.info("Huffman Code | Character")
        # for code in self.m_huffmanCode.keys():
        #     byte = self.m_huffmanCode[code]
        #     self.m_logger.info(f"{code} | {byte}")

        # startTime: float = time.time()
        # self.Decode()
        # endTime: float = time.time()
        # self.m_srcFile.close()
        
        # self.m_logger.info(f"Done decoding. All content saved in {self.m_outFilePath}. Decoding time: {endTime - startTime}s")

    def UpdateReadBuffer(self) -> bool:
        self.m_logger.debug("Trying to update a read buffer...")
        buffer: bytes = self.m_srcFile.read(self.m_srcMaxBufferLength)

        if buffer == b'':
            self.m_logger.debug("Reached end of file")
            return False

        self.m_logger.debug("Read buffer updated!")
        self.m_byteReader.SetBuffer(buffer)
        return True

    def DecodeHuffmanTree(self) -> None:
        self.m_logger.info("Decoding Huffman Tree...")
        huffmanTreeDebug: str = ""
        endOfBufferErrorMessage: str = "Reached end of buffer while decoding Huffman Tree"

        self.UpdateReadBuffer()
        
        # Read process bits (4 bits) + 2
        for _ in range(4):
            self.m_processBits <<= 1
            self.m_processBits |= self.m_byteReader.ReadBit()
        
        self.m_processBits += 2
        self.m_logger.info(f"processBits: {self.m_processBits}")

        # Read unique characters (processBits bits) + 1
        uniqueCharacterCount: int = 0
        for _ in range(self.m_processBits):
            uniqueCharacterCount <<= 1
            uniqueCharacterCount |= self.m_byteReader.ReadBit()

        self.m_logger.info(f"Decoder knows that {self.m_srcFilePath} have {uniqueCharacterCount + 1} unique characters")
        uniqueCharacterCount += 2

        currentNode: binary_tree.Node = self.m_huffmanTreeRootNode
        
        def TryToUpdateBuffer():
            if not self.UpdateReadBuffer():
                self.m_logger.error(endOfBufferErrorMessage)
                assert False, endOfBufferErrorMessage

        def ReadByteWithRetry() -> int:
            result: int = self.m_byteReader.ReadByte()

            if result == -1: # Reached end of buffer. Update Buffer
                self.m_logger.debug("ReadByte. Updating buffer")
                TryToUpdateBuffer()
                
                result: int = self.m_byteReader.ReadByte()

            return result

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
                
                self.m_logger.debug(f"Read 0 from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")
            elif status == 1: # Construct new Node with next byte value
                huffmanTreeDebug += '1'
                self.m_logger.debug(f"Read 1 from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")
                
                textResult: str = ""

                # Check byte size
                if self.m_processBits > 8:
                    bit: int = self.m_byteReader.ReadBit()

                    # size 1
                    if bit == 0:
                        result: int = ReadByteWithRetry()
                        assert result != -1, "Something wrong"
                        textResult += chr(result)
                    elif bit == 1: # size 2
                        result: int = ReadByteWithRetry()
                        assert result != -1, "Something wrong"
                        textResult += chr(result)

                        result: int = ReadByteWithRetry()
                        assert result != -1, "Something wrong"
                        textResult += chr(result)
                else:
                    result: int = ReadByteWithRetry()
                    assert result != -1, "Something wrong"
                    textResult += chr(result)
                
                initialResult: str = textResult
                # Decoding __EOF__
                if textResult in self.m_endOfFile:
                    self.m_logger.debug(f'Found "{textResult}". It may be a part of {self.m_endOfFile}. Decoder will try to investigate it')
                    
                    byteReaderState: byte_reader.ByteReaderState = self.m_byteReader.SaveByteReaderState()
                    
                    for _ in range(len(self.m_endOfFile) - 1 - (len(textResult) - 1)):
                        result = ReadByteWithRetry()
                        
                        textResult += chr(result)
                        if not textResult in self.m_endOfFile:
                            self.m_logger.debug(f"Investigation failed. Returning ByteReader to the previous state. Bad endOfFile={textResult}")
                            self.m_byteReader.LoadByteReaderStat(byteReaderState)
                            textResult = initialResult
                            break
                    
                if textResult == self.m_endOfFile:
                    self.m_logger.debug(f"Found {self.m_endOfFile}")
                
                newNode.m_bytes = textResult
                uniqueCharacterCount -= 1

                huffmanTreeDebug += textResult
                self.m_logger.debug(f"Read {newNode.m_bytes} from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")

                if currentNode.m_left == None:
                    currentNode.AddLeft(newNode)
                elif currentNode.m_right == None:
                    currentNode.AddRight(newNode)
                    while currentNode.m_left != None and currentNode.m_right != None and currentNode.m_parent != None:
                        currentNode.m_bytes = currentNode.m_left.m_bytes + currentNode.m_right.m_bytes
                        currentNode = currentNode.m_parent
            elif status == -1: # Reached end of buffer. Update buffer
                self.m_logger.debug("ReadBit. Updating buffer")
                TryToUpdateBuffer()
        
        self.m_logger.info(f"Decoded Huffman Tree: {huffmanTreeDebug}")

    def ConstructHuffmanCode(self, node: binary_tree.Node, currentCode: str = "") -> None:
        left, right = node.m_left, node.m_right
    
        if left != None:
            self.ConstructHuffmanCode(left, currentCode + '0')

        if right != None:
            self.ConstructHuffmanCode(right, currentCode + '1')

        if node.IsLeaf(): 
            self.m_huffmanCode[currentCode] = node.m_bytes

    def Decode(self) -> None:
        currentCode: str = ""
        writeBuffer: str = ""

        self.m_logger.info("Decoding...")
        with open(self.m_outFilePath, "wb") as outFile:
            while self.m_byteReader.CanRead() or self.UpdateReadBuffer():
                status: int = self.m_byteReader.ReadBit()

                if status == -1:
                    continue
                
                currentCode += str(status)
                if currentCode in self.m_huffmanCode:
                    toWrite: str = self.m_huffmanCode[currentCode]
                    self.m_logger.debug(f'Found {currentCode} in huffman code dictionary. Decoded character: "{toWrite}"')
                    if toWrite == self.m_endOfFile:
                        self.m_logger.debug("Reached EOF")
                        break
                    
                    writeBuffer += toWrite
                    self.m_logger.debug(f"Updated write buffer. Current buffer content: {writeBuffer}")
                    
                    currentCode = ""

                    if len(writeBuffer) > self.m_outMaxBufferLength:
                        self.m_logger.debug(f"Write buffer exceeds max buffer length limit! Writing to {self.m_outFilePath}...")
                        outFile.write(writeBuffer.encode("latin1"))
                        writeBuffer = ""

            if len(writeBuffer) > 0:
                outFile.write(writeBuffer.encode("latin1"))
                writeBuffer = ""

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
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/decoder.log", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    decoder: HuffmanDecoder = HuffmanDecoder(srcFile, outFile)
    decoder.Run()

if __name__ == "__main__":
    main()