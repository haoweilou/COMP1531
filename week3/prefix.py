def prefix_search(dictionary, key_prefix):
    '''
    Given a dictionary (with strings for keys) and a string, returns a 
    new dictionary containing only the keys (and their corresponding values) 
    for which the string is a prefix. If the string is not a prefix for any key, a KeyError is raised.

    For example,
    >>> prefix_search({"ac": 1, "ba": 2, "ab": 3}, "a")
    {'ac': 1, 'ab': 3}
    '''
    new = {}
    for item in dictionary:
        if item.startswith(key_prefix) is True:
            new[item] = dictionary[item]
    if len(new) is 0:
        raise KeyError
    return new
