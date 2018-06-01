#!/usr/bin/python
"""
NAME: Ricardo Kuchimpos,Jesse Catalan
EMAIL: rkuchimpos@gmail.com,jessecatalan77@gmail.com
ID: 704827423,204785152
"""

import sys

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
