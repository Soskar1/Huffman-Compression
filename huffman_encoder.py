from typing import Dict

import binary_tree, byte_analyzer, dynamic_bytes, huffman_code_writer, huffman_header, huffman_tree
import argparse, logging, os, sys

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

    logger: logging.Logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    
    srcMaxBufferLength: int = 1024
    outMaxBufferLength: int = 1024
    byteAnalyzer: byte_analyzer.ByteAnalyzer = byte_analyzer.ByteAnalyzer(srcFile)
    
    logger.info(f"Analyzing {srcFile}...")
    bytePopularity: Dict[chr, int] = byteAnalyzer.Analyze()
    
    logger.info("Constructing Huffman Tree...")
    huffmanTree: binary_tree.Node = huffman_tree.ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, dynamic_bytes.DynamicBytes] = {}
    
    logger.info("Constructing Huffman Code...")
    huffman_tree.ConstructHuffmanCode(huffmanTree, huffmanCode)
    
    logger.debug("Character | Huffman Code | Popularity | ASCII Code")
    for byte in sorted(huffmanCode.keys()):
        code = huffmanCode[byte]
        logger.debug(f"{byte} | {code} | {bytePopularity[byte]} | {ord(byte)}")
    
    logger.info("Constructing Huffman Header...")
    huffmanHeader: huffman_header.HuffmanHeader = huffman_header.HuffmanHeader(huffmanTree, logLevel == 1)
    logger.debug(f"Huffman Header: {huffmanHeader.m_debugHeader}")
    
    codeWriter: huffman_code_writer.HuffmanCodeWriter = huffman_code_writer.HuffmanCodeWriter(huffmanHeader)
    
    if os.path.exists(outFile):
        os.remove(outFile)
    
    logger.info("Encoding...")
    with open(srcFile, "rb") as src:
        readBuffer = src.read(srcMaxBufferLength)
        
        for byte in readBuffer:
            codeWriter.WriteCode(huffmanCode[chr(byte)])
            
            if len(codeWriter.m_buffer) >= outMaxBufferLength:
                with open(outFile, "ab") as out:
                    out.write(codeWriter.m_buffer)
                    codeWriter.m_buffer = ""
    
    codeWriter.End()
    
    if len(codeWriter.m_buffer) > 0:
        with open(outFile, "ab") as out:
            out.write(codeWriter.m_buffer)

    logger.info("Done")

if __name__ == "__main__":
    main()