import binary_tree

def main():
    msg = "aardvark"
    tree = binary_tree.AdaptiveHuffmanTree()
    for symbol in msg:
        tree.AddSymbol(ord(symbol))

    print(msg)

if __name__ == "__main__":
    main()