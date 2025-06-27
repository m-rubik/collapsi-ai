
from collapsi.configs.configs import *

def vprint(*args, **kwargs):
    if PRINT_VERBOSE:
        print(*args, **kwargs)