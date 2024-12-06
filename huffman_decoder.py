import argparse, logging, os, sys

import binary_tree, byte_reader

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

    logger: logging.Logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    
    srcMaxBufferLength: int = 1024
    outMaxBufferLength: int = 1024

    with open(srcFile, "rb") as src:
        uniqueCharacterCount: int = ord(src.read(1))
        logger.info(f"Decoder knows that file contains {uniqueCharacterCount} unique characters")

        logger.info("Decoding Huffman Tree...")
        byteReader: byte_reader.ByteReader = byte_reader.ByteReader()
        rootNode: binary_tree.Node = binary_tree.Node()

        while uniqueCharacterCount > 0:
            readBuffer: bytes = src.read(srcMaxBufferLength)

            if readBuffer == b'':
                logger.error("HUFFMAN TREE DECODING: readBuffer reached the end")
            assert readBuffer != b''

            byteReader.SetBuffer(readBuffer)
            
            status: int = byteReader.ReadBit()
            if status == 0: # Construct empty Node
                pass
            elif status == 1: # Construct new Node with next byte value
                pass
            elif status == -1: # Reached end of buffer. Update buffer
                pass

    # Construct Huffman Tree

    # Create Huffman Code dictionary

    # Decode

if __name__ == "__main__":
    main()