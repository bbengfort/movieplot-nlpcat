__author__ = 'benjamin'

import re
import sys
import string
import unicodedata

from django.utils.encoding import smart_unicode

def slugify_unicode(s):
    chars = []
    for char in unicode(smart_unicode(s)):
        cat = unicodedata.category(char)[0]
        if cat in "LN" or char in "-_~":
            chars.append(char)
        elif cat == "Z":
            chars.append(" ")
    return re.sub("[-\s]+", "-", "".join(chars).strip()).lower()
slugify = slugify_unicode

def remove_punctuation(s):
    if isinstance(s, str):
        return s.translate(string.maketrans("", ""), string.punctuation)
    elif isinstance(s, unicode):
        return s.translate(dict.fromkeys(i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P')))
    else:
        raise TypeError("Could not remove punctuation from type %s" % type(s))