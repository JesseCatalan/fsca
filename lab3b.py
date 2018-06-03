#!/usr/bin/python
"""
NAME: Ricardo Kuchimpos,Jesse Catalan
EMAIL: rkuchimpos@gmail.com,jessecatalan77@gmail.com
ID: 704827423,204785152
"""

import sys

class FileSystemInfo:
    def __init__(self, fs_summary):
        self.fs_summary = fs_summary

    def get_max_block(self):
        superblock = filter(lambda line: line.startswith("SUPERBLOCK"), fs_summary)[0]
        max_block = superblock.split(',')[1] 
        return max_block

class BlockAudit:
    def __init__(self, max_block, fs_summary):
        self.max_block = max_block
        self.blocks = {}
        self.level_name_by_num = {
            0: '',
            1: 'INDIRECT',
            2: 'DOUBLE INDIRECT',
            3: 'TRIPLE INDIRECT'
        }

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
                pass

    def is_invalid(self, block_num):
        return block_num < 0 or block_num > max_block

    def is_reserved(self, block num):
        # know starting point of data block given inode table and
        # total number of inodes
        pass

    def audit(self):
        for block_id, block_stats in self.blocks.items():
            level = self.level_name_by_num[block_stats['block_level']]
            if is_invalid(block_id):
                err_type = 'INVALID'
            if is_reserved(block_id):
                err_type = 'RESERVED'

            print("%s BLOCK %s IN INODE %s AT OFFSET %s"
                    % (err_type, block_num, block_stats['inode_num'],
                        int(block_stats['offset'])))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid number of arguments!\nUsage: ./lab3b [csv]\n")
        exit(1)

    filename = sys.argv[1]
    f = open(filename, 'r')
    fs_summary = f.readlines()
    f.close()

    fsi = FileSystemInfo(fs_summary)
    max_block = fsi.get_max_block()

    exit(0)
