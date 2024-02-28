
def group_by(l, key):
    """ Given a list of objects, returns as a dictionary where the key is the value passed key and the value is the
    object.

    Args:
        rows (list[AvailabilityRow] | list[StationRow]): rows to turn to a dict
        identifier (str): key to group by

    Returns:
        dict: dictionary where key is the value of the passed identifier and the value is the row
    """
    d = {}
    for obj in l:
        key_str = str(obj.__getattribute__(key))
        if key_str in d:
            raise "More than one object has the value {} for key {}".format(key_str, key)
        d[key_str] = obj
    return d