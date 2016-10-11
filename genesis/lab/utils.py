# -*-  coding: utf-8 -*-
"""
"""
import re

tr_to_ascii_trans = str.maketrans('ĞÜŞİÖÇğüşöç', 'GUSIOCgusoc')


def pythonize(s):
    """
    Converts given string in to a form that usable as a Python variable
    """
    # TODO: Not thoroughly tested
    s = s.replace('__', '0SPACE0')
    return re.sub(r'[^0-9a-zA-Z]+', '_', s.strip().translate(tr_to_ascii_trans), re.UNICODE
                  ).replace('0SPACE0', '__')
