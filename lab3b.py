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
        # Key: block number, Value: list of blocks with specified block number
        # Use a list to keep track of duplicates
        self.blocks = {}

        self.free_blocks = []
        self.inodes = {}
        self.free_inodes = []
        self.block_type_by_level = {
            0: 'BLOCK',
            1: 'INDIRECT BLOCK',
            2: 'DOUBLE INDIRECT BLOCK',
            3: 'TRIPLE INDIRECT BLOCK'
        }
        self.fs_summary = fs_summary
        fsi = FileSystemInfo(self.fs_summary)
        self.max_block = fsi.get_max_block()

    def add_block(self, block_num, block_level, inode_num, offset):
        if (block_num == 0):
            return
        block = {
            'block_level': block_level,
            'inode_num': inode_num,
            'offset': offset
        }
        if block_num in self.blocks.keys():
            self.blocks[block_num].append(block)
        else:
            self.blocks[block_num] = [block];

    def parse_blocks(self):
        for entry in fs_summary:
            tokenized = entry.split(',')
            entry_type = tokenized[0]
            if entry_type == 'INDIRECT':
                block_num = int(tokenized[5])
                level = int(tokenized[2])
                inode_num = int(tokenized[1])
                offset = int(tokenized[3])
                self.add_block(block_num, level, inode_num, offset)
            if entry_type == 'INODE':
                inode_num = int(tokenized[1])
                self.inodes[inode_num] = {
                    'links': int(tokenized[6])
                }
                index = 0
                level = 0
                offset = 0
                inode_blocks = tokenized[12:]
                for i_block in inode_blocks:
                    block_num = int(i_block)
                    # offsets calculated based on 1 KiB block size
                    # they can be generalized given the block_size from superblock
                    if index < 12:
                        level = 0
                        offset = index
                    elif index == 12:
                        level = 1
                        offset = 12
                    elif index == 13:
                        level = 2
                        offset = 268
                    elif index == 14:
                        level = 3
                        offset = 65804
                    inode_num = int(tokenized[1])
                    self.add_block(block_num, level, inode_num, offset)
                    index += 1
            if entry_type == 'BFREE':
                self.free_blocks.append(int(tokenized[1]))
            if entry_type == 'IFREE':
                self.free_inodes.append(int(tokenized[1]))

    def is_invalid(self, block_num):
        return block_num < 0 or block_num > self.max_block

    def is_reserved(self, block_num):
        # TODO: Implement.
        # We know starting point of data block given inode table and
        # total number of inodes.
        return 0
    
    def is_unreferenced(self, block_num):
        # Note: this function assumes that legal block checking has occurred
        is_unreferenced = 1
        if block_num in self.blocks or block_num in self.free_blocks:
            is_unreferenced = 0
        return is_unreferenced

    def is_allocated_and_free(self, inode_num):
        # Note: this function assumes that legal block checking has occurred
        is_allocated_and_free = 0
        if inode_num in self.inodes and inode_num in self.free_inodes:
            is_allocated_and_free = 1
        return is_allocated_and_free

    def is_not_allocated_and_not_free(self, inode_num):
        # Note: this function assumes that legal block checking has occurred
        is_not_allocated_and_not_free = 0
        if inode_num not in self.inodes and inode_num not in self.free_inodes:
            is_not_allocated_and_not_free = 1
        return is_not_allocated_and_not_free

    def audit(self):
        for block_num, matching_blocks in self.blocks.items():
            for block_stats in matching_blocks:
                block_type = self.block_type_by_level[block_stats['block_level']]
                inode_num = block_stats['inode_num']
                offset = block_stats['offset']
                if self.is_invalid(block_num):
                    print("INVALID %s %d IN INODE %d AT OFFSET %d"
                            % (block_type, block_num, inode_num, offset))
                if self.is_reserved(block_num):
                    print("RESERVED %s %d IN INODE %d AT OFFSET %d"
                            % (block_type, block_num, inode_num, offset))
                if len(matching_blocks) > 1:
                    print("DUPLICATE %s %d IN INODE %d AT OFFSET %d"
                            % (block_type, block_num, inode_num, offset))
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

