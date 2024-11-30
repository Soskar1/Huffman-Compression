from typing import Dict

import binary_tree, byte_analyzer, dynamic_bytes, huffman_tree
import argparse, os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", help = "Path to the source file")
    args = parser.parse_args()
    
    srcFile: str = args.srcFile
    byteAnalyzer: byte_analyzer.ByteAnalyzer = byte_analyzer.ByteAnalyzer(srcFile)
        
    bytePopularity: Dict[chr, int] = byteAnalyzer.Run()
    
    huffmanTree: binary_tree.Node = huffman_tree.ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, dynamic_bytes.DynamicBytes] = {}
    huffman_tree.ConstructHuffmanCode(huffmanTree, huffmanCode)
    
    for byte in sorted(huffmanCode.keys()):
        code = huffmanCode[byte]
        print(f"{byte}: {code}")