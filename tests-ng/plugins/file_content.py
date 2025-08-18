
""" This function checks each line and return true if the args is found in the file """
def is_line_in_file(fname, value):
    """ Performing unit test to find key/val in files """
    with open(fname, 'r') as file:
        for line in file:
            if value in line.strip():
                return True
    return False
    
                
