#!/usr/bin/env python

# This file is part of dicti.
#
# Project page: https://github.com/tlevine/dicti

# dicti is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# dicti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.

# You should have received a copy of the GNU Affero Public License
# along with dicti.  If not, see <http://www.gnu.org/licenses/>.

# Inspired by Sami but entirely rewritten
# http://code.activestate.com/recipes/66315-case-insensitive-dictionary/

def lower(potentialstring):
    'Lowercase the potential string if possible'
    try:
        return potentialstring.lower()
    except AttributeError:
        return potentialstring

class dicti(dict):
    """
    A dictionary with case-insensitive keys.

    Methods that accept keys do the same thing regardless
    of what case you pass the key in.

    Keys are still stored in their original case, however;
    the original keys are presented when you request them
    with methods like dicti.keys.
    """

    # Implementation: An internal dictionary maps lowercase
    # keys to the original keys. All key lookups are done
    # against the lowercase keys, but all methods that expose
    # keys to the user retrieve the original keys.

#   def __class__(self):
#       return self._keys.__class__()

#   def __cmp__(self):
#       return self._keys.__cmp__()

    def __contains__(self, key):

        k = key.lower()

        return k in self._keys

#   def __delattr__(self):
#       return self._keys.__delattr__()

    def __delitem__(self, k):
        dict.__delitem__(self, self._keys[lower(k)])
        del(self._keys[lower(k)])

#   def __doc__(self):
#       return self._keys.__doc__()

#   def __eq__(self):
#       return self._keys.__eq__()

#   def __format__(self):
#       return self._keys.__format__()

#   def __ge__(self):
#       return self._keys.__ge__()

#   def __getattribute__(self):
#       return self._keys.__getattribute__()

    def __getitem__(self, k):
        """Retrieve the value associated with 'key' (in any case)."""
        return dict.__getitem__(self, self._keys[lower(k)])

#   def __gt__(self):
#       return self._keys.__gt__()

#   def __hash__(self):
#       return self._keys.__hash__()

    def __init__(self, *args, **kwargs):
        # Create the keys dictionary.
        self._keys = {}

        # Create the case-sensitive dictionary.
        fromdict = dict(*args, **kwargs)

        # Update the case-insensitive dictionary.
        self.update(fromdict)

#   def __iter__(self):
#       return self._keys.__iter__()

#   def __le__(self):
#       return self._keys.__le__()

#   def __len__(self):
#       return self._keys.__len__()

#   def __lt__(self):
#       return self._keys.__lt__()

#   def __ne__(self):
#       return self._keys.__ne__()

#   def __new__(self):
#       return self._keys.__new__()

#   def __reduce__(self):
#       return self._keys.__reduce__()

#   def __reduce_ex__(self):
#       return self._keys.__reduce_ex__()

#   def __repr__(self):
#       return self._keys.__repr__()

#   def __setattr__(self):
#       return self._keys.__setattr__()

    def __setitem__(self, k, v):
        self.update({k: v})

#   def __sizeof__(self):
#       return self._keys.__sizeof__()

#   def __str__(self):
#       return self._keys.__str__()

#   def __subclasshook__(self):
#       return self._keys.__subclasshook__()

#   def clear(self):
#       return self._keys.clear()

#   def copy(self):
#       return self._keys.copy()

#   def fromkeys(self):
#       return self._keys.fromkeys()

    def get(self, k, d = None):
        if self.has_key(k):
            return dict.get(self, self._keys[lower(k)], d)
        else:
            return d

    def has_key(self, k):
        return self._keys.has_key(lower(k))

#   def items(self):
#       return self._keys.items()

#   def iteritems(self):
#       return self._keys.iteritems()

#   def iterkeys(self):
#       return self._keys.iterkeys()

#   def itervalues(self):
#       return self._keys.itervalues()

#   def keys(self):
#       return self._keys.keys()

    def pop(self, k, d = None):
        if self.has_key(k):
            return dict.pop(self, self._keys[lower(k)], d)
        else:
            return d

#   def popitem(self):
#       return self._keys.popitem()

    def setdefault(self, key, default):
        """If 'key' doesn't exists, associate it with the 'default' value.
        Return value associated with 'key'."""
        if not self.has_key(key):
            self[key] = default
        return self[key]

    def update(self, d):
        """Copy (key,value) pairs from 'd'."""

        # Remove duplicate keys in the new dictionary
        keys = d.keys()
        keys.reverse()

        so_far = []
        for key in keys:
            l = lower(key)
            if l in so_far:
                del(d[key])
            else:
                so_far.append(l)

        # Remove keys from the old dictionary
        keys_lower = map(lower, d.keys())
        for key_lower in keys_lower:
            if self.has_key(key_lower):
                self.__delitem__(key_lower)

        self._keys.update(dict(zip(keys_lower, d.keys())))

        # Ready
        dict.update(self, d)

#   def values(self):
#       return self._keys.values()

#   def viewitems(self):
#       return self._keys.viewitems()

#   def viewkeys(self):
#       return self._keys.viewkeys()

#   def viewvalues(self):
#       return self._keys.viewvalues()