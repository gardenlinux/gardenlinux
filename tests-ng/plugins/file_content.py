import re
import os

""" This function checks each line and return true if the args is found in the file """
def check_val_in_file(fname, args):
    """ Performing unit test to find key/val in files """
    with open(fname, 'r') as file:
        for line in file:
            if args in line.strip():
                return True
    return False
    
                
