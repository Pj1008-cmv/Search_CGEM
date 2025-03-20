import json
import os.path

class PDS:

    def __init__(self, pds_config_filepath):
        self.pds_config_filepath = pds_config_filepath
        self.rootdir = os.path.dirname(pds_config_filepath)
        self.pds_dict = self.open_pds_config_and_expand_relative_paths(pds_config_filepath)
        
    @staticmethod
    def open_pds_config_and_expand_relative_paths(pds_config_filepath):
        """Read pds_config.json file and expand any relative paths into full paths!"""
        if not os.path.isfile(pds_config_filepath):
            msg = f"ERROR: couldn't find product/derivative/stepping (pds) file: {pds_config_filepath}"
            raise FileNotFoundError(msg)

        # open the pds_config.json file, make all contents instance variables for easy access
        with open(pds_config_filepath, 'r') as pdsconfig:
            pdsdict = json.load(pdsconfig)
        
        rootdir = os.path.dirname(pds_config_filepath)
        pds_dict = {}
        
        for key, value in pdsdict.items():
            pds_dict[key] = value
            if 'stub' in key:
                if 'stub_' in key:
                    fullpathkey = key.replace('stub_', '')
                else:
                    fullpathkey = key.replace('stub ', '' )
                fullpathval = f"{rootdir}\\{value}"
                pds_dict[fullpathkey] = fullpathval
        return pds_dict