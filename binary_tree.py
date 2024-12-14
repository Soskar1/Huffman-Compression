from __future__ import annotations
from typing import Dict

class Node(object):
    def __init__(self, byte: int = 0, count: int = 0):
        self.m_left: Node = None
        self.m_right: Node = None
        self.m_parent: Node = None
        self.m_count: int = count
        self.m_byte: int = byte

    def AddRight(self, node: Node) -> None:
        self.m_right = node
        node.m_parent = self
    
    def AddLeft(self, node: Node) -> None:
        self.m_left = node
        node.m_parent = self
    
    def IsLeaf(self) -> bool:
        if self.m_left == None and self.m_right == None:
            return True
        
        return False

class AdaptiveHuffmanTree(object):
    def __init__(self, reconstructionInterval: int = 1):
        self.m_root: Node = Node(-1, 0)
        self.m_nyt: Node = self.m_root
        self.m_reconstructionInterval: int = reconstructionInterval # TODO
        self.m_symbolNodes: Dict[int, Node] = {}

    def AddSymbol(self, symbol: int) -> None:
        if symbol not in self.m_symbolNodes:
            self.__AddNewSymbol(symbol)
            self.__Update(self.m_nyt.m_parent)
        else:
            symbolNode: Node = self.m_symbolNodes[symbol]
            symbolNode.m_count += 1
            self.__Update(symbolNode)
    
    def GetHuffmanCode(self, symbol: int) -> str:
        if symbol not in self.m_symbolNodes:
            # NYT huffman code + symbol binary
            nytCode: str = self.__ConstructCode(self.m_nyt)
            return nytCode + bin(symbol)[2:].zfill(8)
        
        # symbol huffman code
        return self.__ConstructCode(self.m_symbolNodes[symbol])
    
    def __AddNewSymbol(self, symbol: int) -> None:
        newSymbolNode: Node = Node(symbol, 1)

        newParentNode = Node(0, 1)
        newParentNode.m_left = self.m_nyt
        newParentNode.AddRight(newSymbolNode)
        
        if self.m_nyt == self.m_root:
            self.m_root = newParentNode
        else:
            self.m_nyt.m_parent.AddLeft(newParentNode)
        
        self.m_nyt.m_parent = newParentNode
        self.m_symbolNodes[symbol] = newSymbolNode

    def __Update(self, fromNode: Node) -> None:
        currentNode: Node = fromNode
        while currentNode.m_parent != None:
            parent: Node = currentNode.m_parent
            parent.m_count += 1
            
            if parent.m_left.m_count > parent.m_right.m_count:
                tmp = parent.m_left
                parent.m_left = parent.m_right
                parent.m_right = tmp

            currentNode = parent
    
    def __ConstructCode(self, currentNode: Node) -> str:
        code: str = ""
        while currentNode.m_parent != None:
            parent: Node = currentNode.m_parent
            if currentNode == parent.m_left:
                code += "0"
            elif currentNode == parent.m_right:
                code += "1"
            
            currentNode = parent
        
        return code[::-1]