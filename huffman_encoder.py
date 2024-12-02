from typing import Dict

import binary_tree, byte_analyzer, dynamic_bytes, huffman_code_writer, huffman_header, huffman_tree
import argparse, os

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    parser.add_argument("--debug", "-d", default = False, help = "Turn on debug messages")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    debug: bool = args.debug
    srcMaxBufferLength: int = 1024
    outMaxBufferLength: int = 1024
    byteAnalyzer: byte_analyzer.ByteAnalyzer = byte_analyzer.ByteAnalyzer(srcFile)
    
    print(f"Analyzing {srcFile}...")
    bytePopularity: Dict[chr, int] = byteAnalyzer.Analyze()
    
    print("Constructing Huffman Tree...")
    huffmanTree: binary_tree.Node = huffman_tree.ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, dynamic_bytes.DynamicBytes] = {}
    
    print("Constructing Huffman Code...")
    huffman_tree.ConstructHuffmanCode(huffmanTree, huffmanCode)
    
    if debug:
        print("Huffman Code: ")
        for byte in sorted(huffmanCode.keys()):
            code = huffmanCode[byte]
            print(f"{byte}: {code}")
    
    print("Constructing Huffman Header...")
    huffmanHeader: huffman_header.HuffmanHeader = huffman_header.HuffmanHeader(huffmanTree)
    
    if debug:
        print("Huffman Header: ")
        for byte in huffmanHeader.m_header:
            print(byte)
    
    codeWriter: huffman_code_writer.HuffmanCodeWriter = huffman_code_writer.HuffmanCodeWriter(huffmanHeader, debug=debug)
    
    if os.path.exists(outFile):
        os.remove(outFile)
    
    print("Encoding...")
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

    print("Done")

if __name__ == "__main__":
    main()