import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.batch_loader import batch_loader
def execution():
    batch_loader()

if __name__ == "__main__":
    execution()
