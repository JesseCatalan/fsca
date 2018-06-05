#!/usr/bin/python
"""
NAME: Ricardo Kuchimpos,Jesse Catalan
EMAIL: rkuchimpos@gmail.com,jessecatalan77@gmail.com
ID: 704827423,204785152
"""
import sys
import math

class FileSystemInfo:
    def __init__(self, fs_summary):
        fs_summary = fs_summary
        superblock = filter(lambda line: line.startswith("SUPERBLOCK"), fs_summary)[0]
        superblock_tokens = superblock.split(',')
        self.max_block = int(superblock_tokens[1])
        self.block_size = int(superblock_tokens[3])
        self.first_unreserved_inode = int(superblock_tokens[7])
        
        group_summary = filter(lambda line: line.startswith("GROUP"), fs_summary)[0]
        group_summary_tokens = group_summary.split(',')
        first_inode = int(group_summary_tokens[8])
        inode_size = int(superblock_tokens[4])
        self.num_inodes_in_group = int(group_summary_tokens[3])
        self.first_data_block = first_inode + int(math.ceil(1.0 * self.num_inodes_in_group * inode_size / self.block_size))

    def get_max_block(self):
        return self.max_block

    def get_block_size(self):
        return self.block_size

    # Note: Assume that the file system has only a single block group
    def get_first_data_block(self):
        return self.first_data_block

    def get_first_unreserved_inode(self):
        return self.first_unreserved_inode

    def get_inodes_in_group(self):
        return self.num_inodes_in_group

class Auditor:
    def __init__(self, fs_summary):
        # Key: block number, Value: list of blocks with specified block number
        # Use a list to keep track of duplicates
        self.blocks = {}
        self.free_blocks = []
        self.inodes = {}
        self.free_inodes = []
        self.dirents = {}
        self.parent_dir = {}
        self.references = {}
        self.block_type_by_level = {
            0: 'BLOCK',
            1: 'INDIRECT BLOCK',
            2: 'DOUBLE INDIRECT BLOCK',
            3: 'TRIPLE INDIRECT BLOCK'
        }
        self.fs_summary = fs_summary
        fsi = FileSystemInfo(self.fs_summary)
        self.max_block = fsi.get_max_block()
        self.block_size = fsi.get_block_size()
        self.first_data_block = fsi.get_first_data_block()
        self.pointers_per_block = self.block_size / 4;
        self.first_unreserved_inode = fsi.get_first_unreserved_inode()
        self.max_inode = fsi.get_inodes_in_group()

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
            self.blocks[block_num] = [block]

    def add_dirent(self, parent_inode_num, file_inode_num, filename):
        dirent = {
            'file_inode_num': file_inode_num,
            'filename': filename
        }
        if filename != "'.'" and filename != "'..'":
            self.parent_dir[file_inode_num] = parent_inode_num
        if parent_inode_num in self.dirents.keys():
            self.dirents[parent_inode_num].append(dirent)
        else:
            self.dirents[parent_inode_num] = [dirent]

    def initialize_references(self):
        for inode_num in range (1, self.max_inode + 1):
            self.references[inode_num] = 0

    def parse_blocks(self):
        self.initialize_references()
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
                    if index < 12:
                        level = 0
                        offset = index
                    elif index == 12:
                        level = 1
                        offset = 12
                    elif index == 13:
                        level = 2
                        offset = 12 + self.pointers_per_block
                    elif index == 14:
                        level = 3
                        offset = 12 + self.pointers_per_block + self.pointers_per_block ** 2
                    inode_num = int(tokenized[1])
                    self.add_block(block_num, level, inode_num, offset)
                    index += 1
            if entry_type == 'BFREE':
                self.free_blocks.append(int(tokenized[1]))
            if entry_type == 'IFREE':
                self.free_inodes.append(int(tokenized[1]))
            if entry_type == 'DIRENT':
                parent_inode_num = int(tokenized[1])
                file_inode_num = int(tokenized[3])
                filename = tokenized[6][:-1]
                self.add_dirent(parent_inode_num, file_inode_num, filename)
                if not ((file_inode_num < 0) or (file_inode_num > self.max_inode)):
                    self.references[file_inode_num] += 1

    def is_invalid(self, block_num):
        return block_num < 0 or block_num > self.max_block

    def is_reserved(self, block_num):
        return block_num < self.first_data_block
    
    def is_unreferenced(self, block_num):
        return not (block_num in self.blocks or (block_num in self.free_blocks and len(self.blocks) != 1))

    def block_is_allocated_and_free(self, block_num):
        return block_num in self.blocks and block_num in self.free_blocks

    def inode_is_allocated_and_free(self, inode_num):
        return inode_num in self.inodes and inode_num in self.free_inodes

    def inode_is_not_allocated_and_not_free(self, inode_num):
        return inode_num not in self.inodes and inode_num not in self.free_inodes

    def references_not_equal_links(self, inode_num):
        return self.references[inode_num] != self.inodes[inode_num]['links']

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
                if self.block_is_allocated_and_free(block_num):
                    print("ALLOCATED BLOCK %d ON FREELIST" % (block_num))
        for block_num in range(self.first_data_block, self.max_block):
            if self.is_unreferenced(block_num):
                print ("UNREFERENCED BLOCK %d" % (block_num))
        for inode_num in range(1, self.max_inode):
            if inode_num < self.first_unreserved_inode and inode_num != 2:
                continue
            if self.inode_is_allocated_and_free(inode_num):
                print("ALLOCATED INODE %d ON FREELIST" % (inode_num))
            if self.inode_is_not_allocated_and_not_free(inode_num):
                print("UNALLOCATED INODE %d NOT ON FREELIST" % (inode_num))
        for inode_num in self.inodes:
            if self.references_not_equal_links(inode_num):
                print("INODE %d HAS %d LINKS BUT LINKCOUNT IS %d" % (inode_num, self.references[inode_num], self.inodes[inode_num]['links']))
        for parent_inode_num, dirents in self.dirents.items():
            for dirent in dirents:
                file_inode_num = dirent['file_inode_num']
                filename = dirent['filename']
                if file_inode_num < 1 or file_inode_num > self.max_inode:
                    print("DIRECTORY INODE %d NAME %s INVALID INODE %d" %
                            (parent_inode_num, filename, file_inode_num))
                elif file_inode_num not in self.inodes.keys():
                    print("DIRECTORY INODE %d NAME %s UNALLOCATED INODE %d" %
                            (parent_inode_num, filename, file_inode_num))
                if filename == "'.'":
                    if file_inode_num != parent_inode_num:
                        print("DIRECTORY INODE %d NAME %s LINK TO INODE %d SHOULD BE %d"
                                % (parent_inode_num, filename, file_inode_num, parent_inode_num))
                if filename == "'..'":
                    parent_dir = 2 if parent_inode_num == 2 else self.parent_dir[parent_inode_num]
                    if parent_dir != file_inode_num:
                        print("DIRECTORY INODE %d NAME %s LINK TO INODE %d SHOULD BE %d"
                                % (parent_inode_num, filename, file_inode_num, parent_dir))
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid number of arguments.\nUsage: ./lab3b [csv]\n")
        exit(1)

    filename = sys.argv[1]
    try:
        f = open(filename, 'r')
    except IOError:
        sys.stderr.write("Error. Unable to open file \"%s\".\n" % (filename))
        exit(1)

    fs_summary = f.readlines()
    f.close()

    a = Auditor(fs_summary)
    a.parse_blocks()
    a.audit()

    # TODO: Exit with error code 2 if inconsistencies are found

    exit(0)

