import csv

def csv_to_dict(class_filepath):
    """Turns class.csv into dict (key = vsid) of dicts (subkey = (testtype, corner, core)).
    Data stored in a dictionary, where keys are col headers, values are row-specific.
    """
    class_dict = dict()
    with open(class_filepath, 'r') as f:
        for rowdict in csv.DictReader(f):
            key = rowdict['Visual ID']
            # assemble the per-corner lookup key
            subkey = (rowdict['Test Type'], rowdict['Corner'], str(rowdict['Core/Module Number']))
            # add the row to the data strcture (by key and subkey)
            if key not in class_dict.keys():
                class_dict[key] = dict()
            class_dict[key][subkey] = rowdict
    return class_dict