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
        max_block = int(superblock.split(',')[1])
        return max_block

class BlockAudit:
    def __init__(self, fs_summary):
        self.blocks = {}
        self.block_type_by_level = {
            0: 'BLOCK',
            1: 'INDIRECT BLOCK',
            2: 'DOUBLE INDIRECT BLOCK',
            3: 'TRIPLE INDIRECT BLOCK'
        }

        self.fs_summary = fs_summary
        fsi = FileSystemInfo(self.fs_summary)
        self.max_block = fsi.get_max_block()

    def parse_blocks(self):
        for entry in fs_summary:
            tokenized = entry.split(',')
            if tokenized[0] == 'INDIRECT':
                block_num = int(tokenized[5])
                self.blocks[block_num] = {
                    'block_level': int(tokenized[2]),
                    'inode_num': int(tokenized[1]),
                    'offset': int(tokenized[3])
                }
            if tokenized[0] == 'INODE':
                inode_blocks = tokenized[12:]
                for i_block in inode_blocks:
                    block_num = int(i_block)
                    self.blocks[block_num] = {
                        'block_level': 0,
                        'inode_num': int(tokenized[1]),
                        'offset': (block_num * 512)
                    }
            if tokenized[0] == 'BFREE':
                pass
            if tokenized[1] == 'IFREE':
                pass

    def is_invalid(self, block_num):
        return block_num < 0 or block_num > self.max_block

    def is_reserved(self, block_num):
        # TODO: Implement.
        # We know starting point of data block given inode table and
        # total number of inodes.
        return 0

    def audit(self):
        for block_num, block_stats in self.blocks.items():
            block_type = self.block_type_by_level[block_stats['block_level']]
            err_type = None
            if self.is_invalid(block_num):
                err_type = 'INVALID'
            if self.is_reserved(block_num):
                err_type = 'RESERVED'

            if err_type is not None:
                print("%s %s %s IN INODE %s AT OFFSET %s"
                        % (err_type, block_type, block_num, block_stats['inode_num'],
                            block_stats['offset']))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid number of arguments!\nUsage: ./lab3b [csv]\n")
        exit(1)

    filename = sys.argv[1]
    f = open(filename, 'r')
    fs_summary = f.readlines()
    f.close()

    ba = BlockAudit(fs_summary)
    ba.parse_blocks()
    ba.audit()

    exit(0)
