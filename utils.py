import os
import sys
import types
import traceback

from data import DataLoader
from features import FeatureParser
from constants import TRACEBACK_LIMIT


def exec_user_code(code, module_name="feature_trans"):

    user_module_path = os.path.join(".", ".%s.py" % (module_name,))

    mod = types.ModuleType(module_name)
    mod.__file__ = user_module_path
    sys.modules[module_name] = mod

    exec(code, mod.__dict__)

    return mod


def complete_feature_code(user_code):

    import_statements = """from features import FeatureDef;import numpy as np;"""

    feature_def_elements = user_code.split(";")[:-1]  # ELIMINATE POSSIBLE STUFF AFTER THE LAST SEMICOLON

    feature_list_code = "features = ["+",".join(feature_def_elements)+"]"

    return import_statements+feature_list_code


def get_data(url):
    data_loader = DataLoader(local_data_dir="./data")
    return data_loader.load_data(data_path=url)


def encode_target(raw_target):

    encoded_target = raw_target.astype(int)

    unique_target_values = encoded_target.unique()
    n_classes = len(unique_target_values)

    target_value_lookup = {true_target_value: target_value_code
                           for target_value_code, true_target_value in enumerate(sorted(unique_target_values))}

    for i, value in enumerate(encoded_target):
        encoded_target[i] = target_value_lookup[value]

    return encoded_target, n_classes


def construct_parser(code_raw_string):

    complete_code = complete_feature_code(user_code=code_raw_string)
    module_with_user_code = exec_user_code(code=complete_code)

    feature_list = getattr(module_with_user_code, "features")

    if len(feature_list) == 0:
        raise ValueError("Provided feature list is empty! Check your feature definition code.")
    else:
        return FeatureParser(features=feature_list), complete_code


def error_with_traceback(error):
    return {"error": error,
            "traceback": traceback.format_exc(limit=TRACEBACK_LIMIT)}
