from collections import defaultdict


def create_nested_dict():
    nested_dict = lambda: defaultdict(nested_dict)
    return nested_dict()