#!/usr/bin/python
"""
NAME: Ricardo Kuchimpos,Jesse Catalan
EMAIL: rkuchimpos@gmail.com,jessecatalan77@gmail.com
ID: 704827423,204785152
"""

import sys


class BlockAudit:
    def __init__(self, max_block, fs_summary):
        self.max_block = max_block
        self.blocks = {}

    def parse_blocks(self):
        for entry in fs_summary:
            tokenized = entry.split(',')
            if tokenized[0] == 'INDIRECT':
                block_num = tokenized[5]
                self.blocks[block_num] = {
                    'block_level': tokenized[2],
                    'inode_num': tokenized[1],
                    'offset': tokenized[3]
                }
            if tokenized[0] == 'INODE':
                inode_blocks = tokenized[12:]
                for i_block in inode_blocks:
                    self.blocks[i_block] = {
                        'block_level': 1,
                        'inode_num': tokenized[1],
                        'offset': i_block * 512
                    }
            if tokenized[0] == 'BFREE':
                pass
            if tokenized[1] == 'IFREE':
                pass


    def is_invalid(self, block_num):
        return block_num < 0 or block_num > max_block

    def is_reserved(self, block num):
        # know starting point of data block given inode table and
        # total number of inodes
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid number of arguments!\nUsage: ./lab3b [csv]\n")
        exit(1)

    filename = sys.argv[1]
    f = open(filename, 'r')
    fs_summary = f.readlines()
    f.close()

    superblock = filter(lambda line: line.startswith("SUPERBLOCK"), fs_summary)
    indirect_blocks = filter(lambda line: line.startswith("INDIRECT"), fs_summary)
    inodes = filter(lambda line: line.startswith("INODE"), fs_summary)
    free_blocks = filter(lambda line: line.startswith("BFREE"), fs_summary)
    free_inodes = filter(lambda line: line.startswith("IFREE"), fs_summary)
    dirents = filter(lambda line: line.startswith("DIRENT"), fs_summary)
    groups = filter(lambda line: line.startswith("GROUP"), fs_summary)


    exit(0)
