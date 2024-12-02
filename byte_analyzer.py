import os
from typing import Dict, List

class ByteAnalyzer(object):
    def __init__(self, fileName: str, bufferSize: int = 8192):
        self.m_bufferSize = bufferSize
        self.m_fileName = fileName

    def Analyze(self) -> Dict[chr, int]:
        bytePopularity: Dict[chr, int] = {}

        with open(self.m_fileName, "rb") as file:
            while True:
                buffer = file.read(self.m_bufferSize)
                
                if (buffer == b''):
                    break
                
                for byte in buffer:
                    byte = chr(byte)

                    if byte not in bytePopularity:
                        bytePopularity[byte] = 0
                    
                    bytePopularity[byte] += 1

        return bytePopularity

def ListFilesRecursive(path: str = '.') -> List[str]:
    files: List[str] = []

    for entry in os.listdir(path):
        fullPath: str = os.path.join(path, entry)
        if os.path.isdir(fullPath):
            try:
                files.extend(ListFilesRecursive(fullPath))
            except:
                pass
        else:
            print("Appending {0}".format(fullPath))
            files.append(fullPath)

    return files


if __name__ == "__main__":
    files = ListFilesRecursive("For analyzing\\")
    bytePopularity = {}
    totalBytes = 0

    for file in files:
        print("Analyzing {0}".format(file))
        analyzer = ByteAnalyzer(file)
        result = analyzer.Analyze()

        for item in result.items():
            byte, count = item[0], item[1]
            if byte in bytePopularity:
                bytePopularity[byte] += count
            else:
                bytePopularity[byte] = count

            totalBytes += count

    print("==========================================")
    print("Result:\n{0}MB read\n{1} unique characters".format(totalBytes / 1000000, len(bytePopularity)))
    print("==========================================")
    bytePopularity = dict(sorted(bytePopularity.items(), key=lambda item: item[1], reverse=True))

    for byte in bytePopularity.keys():
        print("{0} ({1} | {2:08b}): {3} {4}%".format(byte, ord(byte), ord(byte), bytePopularity[byte], bytePopularity[byte] / totalBytes * 100))
