from typing import Dict

import binary_tree, byte_reader, byte_writer
import argparse, collections, io, logging, sys, time

class HuffmanDecoder(object):
    def __init__(self, srcFilePath: str, outFilePath: str, srcMaxBufferLength: int = 1024, outMaxBufferLength: int = 1024, debug: bool = False):
        self.m_srcFilePath: str = srcFilePath
        self.m_outFilePath: str = outFilePath
        self.m_srcFile: io.BufferedReader = None

        self.m_srcMaxBufferLength: int = srcMaxBufferLength
        self.m_outMaxBufferLength: int = outMaxBufferLength
        
        self.m_byteReader: byte_reader.ByteReader = byte_reader.ByteReader(debug=debug)
        self.m_huffmanTreeRootNode: binary_tree.Node = binary_tree.Node()
        self.m_huffmanCode: Dict[str, str] = {}
        
        self.m_processBits: int = 0
        self.m_paddingZeros: int = 0

        self.m_debug: bool = debug
        self.m_logger: logging.Logger = logging.getLogger(__name__)
        self.m_logger.addHandler(logging.StreamHandler(sys.stdout))

    def Run(self) -> None:
        self.m_srcFile = open(self.m_srcFilePath, "rb")
        self.DecodeHeader()

        self.m_logger.info("Constructing Huffman Code...")
        self.ConstructHuffmanCode(self.m_huffmanTreeRootNode)

        self.m_logger.info("Huffman Code | Character")
        for code in self.m_huffmanCode.keys():
            byte = self.m_huffmanCode[code]
            self.m_logger.info(f"{code} | {byte:0{self.m_processBits}b}")

        startTime: float = time.time()
        self.DecodeSourceFile()
        endTime: float = time.time()
        
        self.m_srcFile.close()
        self.m_logger.info(f"Done decoding. All content saved in {self.m_outFilePath}. Decoding time: {endTime - startTime}s")

    def UpdateReadBuffer(self) -> bool:
        if self.m_debug:
            self.m_logger.debug("Trying to update a read buffer...")
        buffer: bytes = self.m_srcFile.read(self.m_srcMaxBufferLength)

        if buffer == b'':
            if self.m_debug:
                self.m_logger.debug("Reached end of file")
            
            return False

        if self.m_debug:
            self.m_logger.debug("Read buffer updated!")
        
        self.m_byteReader.SetBuffer(buffer)
        return True

    def DecodeHeader(self) -> None:
        self.m_logger.info("Decoding Huffman Tree...")
        huffmanTreeDebug: str = ""
        endOfBufferErrorMessage: str = "Reached end of buffer while decoding Huffman Tree"

        self.UpdateReadBuffer()

        # First 4 bits = process Bits
        for _ in range(4):
            bit: int = self.m_byteReader.ReadBit()
            self.m_processBits <<= 1
            self.m_processBits |= bit

        self.m_processBits += 2

        # 3 bits = padding zeros at the end of file
        for _ in range(3):
            bit: int = self.m_byteReader.ReadBit()
            self.m_paddingZeros <<= 1
            self.m_paddingZeros |= bit
        
        # 4 bits = padding zeros in byte
        bytePaddingZeros: int = 0
        for _ in range(4):
            bit: int = self.m_byteReader.ReadBit()
            bytePaddingZeros <<= 1
            bytePaddingZeros |= bit
        
        self.m_paddingZeros += bytePaddingZeros

        if self.m_debug:
            self.m_logger.debug(f"processBits: {self.m_processBits}")
            self.m_logger.debug(f"Padding zero's: {self.m_paddingZeros}")

        currentNode: binary_tree.Node = self.m_huffmanTreeRootNode
        
        def TryToUpdateBuffer() -> bool:
            if not self.UpdateReadBuffer():
                self.m_logger.error(endOfBufferErrorMessage)
                assert False, endOfBufferErrorMessage

            return True

        while True:
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
                
                if self.m_debug:
                    self.m_logger.debug(f"Read 0 from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")
            elif status == 1: # Construct new Node with next byte value
                huffmanTreeDebug += '1'
                
                if self.m_debug:
                    self.m_logger.debug(f"Read 1 from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")
                
                byte: int = 0
                for _ in range(self.m_processBits):
                    result: int = self.m_byteReader.ReadBit()

                    if result == -1:
                        if TryToUpdateBuffer():
                            result = self.m_byteReader.ReadBit()
                        else:
                            assert False, "Something is wrong"
                        
                    byte <<= 1
                    byte |= result
                
                newNode.m_byte = byte
                huffmanTreeDebug += bin(byte)[2:].rjust(self.m_processBits, '0')
                
                if self.m_debug:
                    self.m_logger.debug(f"Read {newNode.m_byte} from HuffmanTree. Current huffman tree code: {huffmanTreeDebug}")

                if currentNode.m_left == None:
                    currentNode.AddLeft(newNode)
                elif currentNode.m_right == None:
                    currentNode.AddRight(newNode)
                    while currentNode.m_left != None and currentNode.m_right != None and currentNode.m_parent != None:
                        currentNode.m_byte = currentNode.m_left.m_byte + currentNode.m_right.m_byte
                        currentNode = currentNode.m_parent

                    if currentNode.m_parent == None and currentNode.m_left != None and currentNode.m_right != None:
                        # Reached root. Need to end tree construction
                        break
            elif status == -1: # Reached end of buffer. Update buffer
                if self.m_debug:
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
            self.m_huffmanCode[currentCode] = node.m_byte

    def DecodeSourceFile(self) -> None:
        currentCode: str = ""
        byteWriter: byte_writer.ByteWriter = byte_writer.ByteWriter(debug=self.m_debug)
        codeHistory: collections.deque = collections.deque([])
        codeHistoryCapacity: int = 8

        self.m_logger.info("Decoding...")
        with open(self.m_outFilePath, "wb") as outFile:
            while self.m_byteReader.CanRead() or self.UpdateReadBuffer():
                status: int = self.m_byteReader.ReadBit()

                if status == -1:
                    continue
                
                currentCode += str(status)
                
                if self.m_debug:
                    self.m_logger.debug(f"Current code: {currentCode}")
                
                if currentCode in self.m_huffmanCode:
                    byte: int = self.m_huffmanCode[currentCode]
                    
                    if self.m_debug:
                        self.m_logger.debug(f'Found {currentCode} in huffman code dictionary. Decoded character: "{byte:0{self.m_processBits}b}"')

                    byteWriter.WriteBitsFromByte(byte, self.m_processBits)

                    codeHistory.append(currentCode)
                    if len(codeHistory) > codeHistoryCapacity:
                        codeHistory.popleft()
                    
                    currentCode = ""

                    if len(byteWriter.m_buffer) > self.m_outMaxBufferLength:
                        if self.m_debug:
                            self.m_logger.debug(f"Write buffer exceeds max buffer length limit! Writing to {self.m_outFilePath}...")
                        
                        content: bytearray = byteWriter.PopContent()
                        outFile.write(content)

            assert '1' not in currentCode
            self.m_paddingZeros -= len(currentCode)

            if self.m_paddingZeros > 0:
                if self.m_debug:
                    self.m_logger.debug(f"{self.m_paddingZeros} padding zeros left")

                while self.m_paddingZeros and '1' not in codeHistory[-1]:
                    lastCode = codeHistory[-1]
                    codeHistory.pop()

                    lastByte: int = self.m_huffmanCode[lastCode]
                    byteStr: str = bin(lastByte)[2:]
                    byteLength: int = len(byteStr)
                    amountOfZeros: int = byteStr.count('0')

                    if self.m_debug:
                        self.m_logger.debug(f"Last used huffman code: {lastCode} ({lastByte:0{self.m_processBits}b}). Byte length to delete from buffer: {byteLength}")
                    
                    if self.m_paddingZeros != amountOfZeros:
                        while byteLength > 0:
                            byteWriter.DeleteLastBit()
                            byteLength -= 1
                        self.m_paddingZeros -= len(lastCode)
                    else:
                        byteLength = amountOfZeros
                        while byteLength > 0:
                            byteWriter.DeleteLastBit()
                            byteLength -= 1
                        self.m_paddingZeros = 0
                    
                    if self.m_debug:
                        self.m_logger.debug(f"{self.m_paddingZeros} padding zeros left")

                while self.m_paddingZeros > 0:
                    byteWriter.DeleteLastBit()
                    self.m_paddingZeros -= 1

                    if self.m_debug:
                        self.m_logger.debug(f"{self.m_paddingZeros} padding zeros left")

            if len(byteWriter.m_buffer) > 0:
                content: bytearray = byteWriter.PopContent(getAll=True)
                outFile.write(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("-l", "--logLevel", type = int, default = 2, help = "To configure logging messages. 1 - DEBUG, 2 - INFO, 3 - WARNING, 4 - ERROR, 5 - CRITICAL")
    args = parser.parse_args()

    srcFile: str = args.srcFile
    outFile: str = args.outFile
    logLevel: int = args.logLevel
    
    if logLevel <= 0 or logLevel > 5:
        raise Exception("Bad logLevel")
    
    logging.basicConfig(level = logLevel * 10, filename = "logs/decoder.log", filemode = "w",
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    decoder: HuffmanDecoder = HuffmanDecoder(srcFile, outFile, debug = logLevel == 1)
    decoder.Run()

if __name__ == "__main__":
    main()