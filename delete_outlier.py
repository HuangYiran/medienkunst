import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--foldA',
        default='/Users/ihuangyiran/Documents/Workplace_Python/data/pix2pix/edge/val',
        help='foldA is in foldB')
parser.add_argument('--foldB',
        default='/Users/ihuangyiran/Documents/Workplace_Python/data/pix2pix/origin/val',
        help='foldA is in foldB')
opt = parser.parse_args()

sur_dir = opt.foldA
tgt_dir = opt.foldB

filesA = []
filesB = []

for root, dir, files in os.walk(sur_dir):
    for file in files:
        filesA.append(file)

for root, dir, files in os.walk(tgt_dir):
    for file in files:
        filesB.append(file)

for file in filesB:
    if not file in filesA:
        print (file +" is not in fileA, so delete the file")
        os.remove(tgt_dir + '/' + file)
