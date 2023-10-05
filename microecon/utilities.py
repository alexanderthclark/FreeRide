'''
Utility functions
'''
import numpy as np


def args_to_array(args):
    """
    When args is a tuple of scalars, this returns them in one array.
    When args' first element is iterable, this returns the first element.
    """
    # check for iterable
    if np.iterable(args[0]) and len(args) == 1:
        a = args[0]
    elif np.iterable(args[0]):
        raise ValueError("Unexpected input. args should be a tuple of scalars or a single array")
    else:
        a = tuple(args)
    return a

