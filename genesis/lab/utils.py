# -*-  coding: utf-8 -*-
"""
"""
import re

tr_to_ascii_trans = str.maketrans('ĞÜŞİÖÇğüşöçı', 'GUSIOCgusoci')


def pythonize(s):
    """
    Converts given string in to a form that usable as a Python variable
    """
    # TODO: Not thoroughly tested
    s = s.replace('__', '0SPACE0')
    return re.sub(r'[^0-9a-zA-Z]+', '_', s.strip().translate(tr_to_ascii_trans), re.UNICODE
                  ).replace('0SPACE0', '__')


class lazy_property(object):
    """
    Meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.

    from: http://stackoverflow.com/a/6849299/454130
    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        obj.__dict__[self.func_name] = value
        return value


def tupper(w):
    return w.replace('i', 'İ').replace('ı', 'I').upper()


def tlower(w):
    return w.replace('I', 'ı').replace('İ', 'i').lower()
