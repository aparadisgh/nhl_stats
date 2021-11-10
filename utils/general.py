
def convert_to_flat_dict(my_dict, existing_dict, delimiter="_", prefix=""):
    
    for k, v in my_dict.items():
        if not isinstance(v, dict):
            existing_dict[prefix + k] = v
        else:
            convert_to_flat_dict(v, existing_dict, delimiter, prefix + k + delimiter)
    return existing_dict
