import re
import os


def file_content(fname, args):
    """ Performing unit test to find key/val in files """
    with open(fname, 'r') as file:
        for line in file:
            if args in line.strip():
                return True
        return False
    
                
