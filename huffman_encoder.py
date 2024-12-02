from typing import Dict

import binary_tree, byte_analyzer, dynamic_bytes, huffman_code_writer, huffman_tree
import argparse

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    parser.add_argument("outFile", help = "Path to the out file")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    outFile: str = args.outFile
    srcMaxBufferLength = 1024
    outMaxBufferLength = 1024
    byteAnalyzer: byte_analyzer.ByteAnalyzer = byte_analyzer.ByteAnalyzer(srcFile)
        
    bytePopularity: Dict[chr, int] = byteAnalyzer.Analyze()
    
    huffmanTree: binary_tree.Node = huffman_tree.ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, dynamic_bytes.DynamicBytes] = {}
    huffman_tree.ConstructHuffmanCode(huffmanTree, huffmanCode)
    
    for byte in sorted(huffmanCode.keys()):
        code = huffmanCode[byte]
        print(f"{byte}: {code}")
    
    codeWriter: huffman_code_writer.HuffmanCodeWriter = huffman_code_writer.HuffmanCodeWriter()
    
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

if __name__ == "__main__":
    main()