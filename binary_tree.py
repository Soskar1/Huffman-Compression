from __future__ import annotations

class Node(object):
    def __init__(self):
        self.m_left: Node = None
        self.m_right: Node = Node
        self.m_code: int = 0
        self.m_byte: int = 0

    def AddRight(self, node: Node) -> None:
        self.m_right = node
    
    def AddLeft(self, node: Node) -> None:
        self.m_left = node
