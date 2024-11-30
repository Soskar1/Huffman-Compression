from binary_tree import Node
from typing import Dict, List

def ConstructHuffmanTree(bytePopularity: Dict[str, int]) -> Node:
    leafs: List[Node] = []

    for item in bytePopularity.items():
        byte, count = item[0], item[1]
        node: Node = Node(byte, count)

        leafs.append(node)
    
    while len(leafs) > 1:
        leafs = sorted(leafs, key = lambda leaf: leaf.m_count)

        left: Node = leafs.pop(0)
        right: Node = leafs.pop(0)
         
        newByte: str = left.m_bytes + right.m_bytes
        newCount: int = left.m_count + right.m_count
        
        newNode: Node = Node(newByte, newCount)
        newNode.AddLeft(left)
        newNode.AddRight(right)
        
        leafs.append(newNode)

    root: Node = leafs.pop(0)
    return root

def ConstructHuffmanCode(node: Node, coding: Dict[str, bytearray], currentCode: bytearray = bytearray([1])) -> None:
    left, right = node.m_left, node.m_right
    
    if left != None:
        ConstructHuffmanCode(left, coding, currentCode[0] << 1)
    
    if right != None:
        ConstructHuffmanCode(right, coding, (currentCode[0] << 1) + 1)
    
    if node.IsLeaf(): 
        coding[node.m_bytes] = currentCode

if __name__ == "__main__":
    bytePopularity: Dict[str, int] = {
        "A": 4,
        "B": 2,
        "C": 3,
        "D": 1,
        "E": 6,
        "F": 3,
        "G": 9,
        "H": 4,
        "I": 2,
        "J": 7,
        "J": 3,
        "K": 10,
        "L": 11,
        "M": 9,
        "N": 1,
        "O": 3,
        "P": 2,
        "Q": 5,
        "R": 4,
        "S": 7,
        "T": 8,
        "U": 6,
        "V": 1,
        "T": 2,
        "W": 6,
        "X": 9,
        "Y": 8,
        "Z": 1,
        "a": 1,
        "b": 1,
        "c": 1,
        "d": 1,
        "e": 1,
        "f": 1,
        "g": 1,
        "h": 1,
        "i": 1,
        "j": 1,
        "k": 1,
        "l": 1,
        "m": 1,
        "n": 1,
        "o": 1,
        "p": 1,
        "q": 1,
        "r": 1,
        "s": 1,
        "t": 1,
        "u": 1,
        "v": 1,
        "w": 1,
        "x": 1,
        "y": 1,
        "z": 1,
    }
    
    root: Node = ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, bytearray] = {}
    ConstructHuffmanCode(root, huffmanCode)
    
    for byte in sorted(huffmanCode.keys()):
        code = huffmanCode[byte]
        print(f"{byte}: {code}")