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

def ConstructHuffmanCode(node: Node, coding: Dict[str, int], currentCode: chr = 0) -> None:
    left, right = node.m_left, node.m_right
    
    if left != None:
        ConstructHuffmanCode(left, coding, currentCode << 1)
    
    if right != None:
        ConstructHuffmanCode(right, coding, (currentCode << 1) + 1)
    
    if node.IsLeaf(): 
        coding[node.m_bytes] = currentCode

if __name__ == "__main__":
    bytePopularity: Dict[str, int] = {
        "A": 4,
        "B": 2,
        "C": 3,
        "D": 1
    }
    
    root: Node = ConstructHuffmanTree(bytePopularity)
    huffmanCode: Dict[str, int] = {}
    ConstructHuffmanCode(root, huffmanCode)
    
    for item in huffmanCode.items():
        byte, code = item[0], item[1]
        print(f"{byte}: {bin(code)}")