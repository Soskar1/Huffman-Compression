from __future__ import annotations

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