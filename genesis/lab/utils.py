# -*-  coding: utf-8 -*-
"""
"""
import re

tr_to_ascii_trans = bytes.maketrans('ĞÜŞİÖÇğüşöç', 'GUSIOCgusoc')


def pythonize(s):
    """
    Converts given string in to a form that usable as a Python variable
    """
    # TODO: Not thoroughly tested
    return re.sub(r'[^0-9a-zA-Z]+', '_', s.strip().translate(tr_to_ascii_trans), re.UNICODE)
