from binary_tree import Node

class HuffmanHeader(object):
    def __init__(self, huffmanTreeRoot: Node):
        self.m_header: bytearray = bytearray()
        self.m_maxBits: int = 8
        self.m_freeBits: int = 8
        self.m_notFilledByte: chr = 0b0

        self.m_debugHeader: str = ""
        
        self.TraverseHuffmanTree(huffmanTreeRoot)
        if self.m_notFilledByte != 0b0:
            self.CreateByte()
        
    def CreateByte(self) -> None:
        self.m_header.append(self.m_notFilledByte)
        self.m_notFilledByte = 0b0
        self.m_freeBits = self.m_maxBits

    def TraverseHuffmanTree(self, node: Node) -> None:
        if not node.IsLeaf() and not node.m_isRoot:
            self.AppendBit(0)
        
        if node.m_left != None:
            self.TraverseHuffmanTree(node.m_left)
            
        if node.m_right != None:
            self.TraverseHuffmanTree(node.m_right)
            
        if node.IsLeaf():
            self.AppendBit(1)
            
            for byte in node.m_bytes:
                self.AppendByte(ord(byte))
            
    def AppendBit(self, bit: bool) -> None:
        if bit == 0:
            self.m_debugHeader += '0'
        
        if bit == 1:
            self.Append1Bit()
            self.m_debugHeader += '1'
        
        self.m_freeBits -= 1
        if self.m_freeBits == 0:
            self.CreateByte()
        
    def Append1Bit(self) -> None:
        if self.m_freeBits == 8:
            self.m_notFilledByte |= 0b10000000
        if self.m_freeBits == 7:
            self.m_notFilledByte |= 0b1000000
        if self.m_freeBits == 6:
            self.m_notFilledByte |= 0b100000
        if self.m_freeBits == 5:
            self.m_notFilledByte |= 0b10000
        if self.m_freeBits == 4:
            self.m_notFilledByte |= 0b1000
        if self.m_freeBits == 3:
            self.m_notFilledByte |= 0b100
        if self.m_freeBits == 2:
            self.m_notFilledByte |= 0b10
        if self.m_freeBits == 1:
            self.m_notFilledByte |= 0b1
    
    def AppendByte(self, byte: chr) -> None:
        self.m_debugHeader += chr(byte)

        if self.m_freeBits == self.m_maxBits:
            self.m_header.append(byte)
        else:    
            byteLength = self.m_maxBits
            tmp: chr = 0b0
            tmpLength: int = byteLength - self.m_freeBits
            while byteLength > self.m_freeBits:
                tmp >>= 1
                
                if byte & 0b1 == 0b1:
                    tmp |= 0b10000000
                
                byte >>= 1
                byteLength -= 1
                
            self.m_notFilledByte |= byte
            self.CreateByte()            
            
            self.m_notFilledByte = tmp
            self.m_freeBits = self.m_maxBits - tmpLength