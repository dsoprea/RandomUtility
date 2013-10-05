###############################################################################
# Copyright (C) 2013 Dustin Oprea                                             #
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher       #
# based on code in "django-passwords" by Donald Stufft                        #
# (https://github.com/dstufft/django-passwords/blob/master/passwords/         #
#  validators.py)                                                             #
# See https://github.com/dsoprea/RandomUtility for the full collection of     #
# tools.                                                                      #
###############################################################################

from __future__ import division
from string import punctuation

class ValidationError(Exception):
    def __init__(self, message, code=None):
        self.__code = code
        super(ValidationError, self).__init__(message)

    @property
    def code(self):
        return self.__code

# Python3 doesn't have "unicode" (all strings are unicode).

try:
    unicode
except NameError:
    unicode = str

# Python3 doesn't have "xrange".

try:
    xrange
except NameError:
    xrange = range

_ = unicode

def smart_unicode(data):
    if issubclass(data.__class__, unicode):
        return data

    return data.decode('ascii')

PASSWORD_COMMON_SEQUENCES = [ "0123456789",
                              "`1234567890-=",
                              "~!@#$%^&*()_+",
                              "abcdefghijklmnopqrstuvwxyz",
                              "quertyuiop[]\\asdfghjkl;\'zxcvbnm,./",
                              'quertyuiop{}|asdfghjkl;"zxcvbnm<>?',
                              "quertyuiopasdfghjklzxcvbnm",
                              "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
                              "qazwsxedcrfvtgbyhnujmikolp" ]

class LengthValidator(object):
    message = _("Invalid Length (%s)")
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                self.message % _("Must be %s characters or more") % self.min_length,
                code=self.code)
        elif self.max_length and len(value) > self.max_length:
            raise ValidationError(
                self.message % _("Must be %s characters or less") % self.max_length,
                code=self.code)

class ComplexityValidator(object):
    message = _("Must be more complex (%s)")
    code = "complexity"

    def __init__(self, complexities):
        self.complexities = complexities

    def __call__(self, value):
        if self.complexities is None:
            return

        uppercase, lowercase, digits, non_ascii, punctuation_ = set(), set(), set(), set(), set()

        for character in value:
            if ord(character) >= 128:
                non_ascii.add(character)
            elif character.isupper():
                uppercase.add(character)
            elif character.islower():
                lowercase.add(character)
            elif character.isdigit():
                digits.add(character)
            elif character in punctuation:
                punctuation_.add(character)
            else:
                non_ascii.add(character)

        words = set(value.split())

        if len(uppercase) < self.complexities.get("UPPER", 0):
            raise ValidationError(
                self.message % _("Must contain %(UPPER)s or more unique uppercase characters") % self.complexities,
                code=self.code)
        elif len(lowercase) < self.complexities.get("LOWER", 0):
            raise ValidationError(
                self.message % _("Must contain %(LOWER)s or more unique lowercase characters") % self.complexities,
                code=self.code)
        elif len(digits) < self.complexities.get("DIGITS", 0):
            raise ValidationError(
                self.message % _("Must contain %(DIGITS)s or more unique digits") % self.complexities,
                code=self.code)
        elif len(punctuation_) < self.complexities.get("PUNCTUATION", 0):
            raise ValidationError(
                self.message % _("Must contain %(PUNCTUATION)s or more unique punctuation character") % self.complexities,
                code=self.code)
        elif len(non_ascii) < self.complexities.get("NON ASCII", 0):
            raise ValidationError(
                self.message % _("Must contain %(NON ASCII)s or more unique non ascii characters") % self.complexities,
                code=self.code)
        elif len(words) < self.complexities.get("WORDS", 0):
            raise ValidationError(
                self.message % _("Must contain %(WORDS)s or more unique words") % self.complexities,
                code=self.code)


class BaseSimilarityValidator(object):
    message = _("Too Similar to [%(haystacks)s]")
    code = "similarity"

    def __init__(self, haystacks=None, password_match_threshold=0.9):
        self.haystacks = haystacks if haystacks else []
        self.__password_match_threshold = password_match_threshold

    def fuzzy_substring(self, needle, haystack):
        needle, haystack = needle.lower(), haystack.lower()
        m, n = len(needle), len(haystack)

        if m == 1:
            if not needle in haystack:
                return -1
        if not n:
            return m

        row1 = [0] * (n+1)
        for i in xrange(0,m):
            row2 = [i+1]
            for j in xrange(0,n):
                cost = ( needle[i] != haystack[j] )
                row2.append(min(row1[j+1]+1, row2[j]+1, row1[j]+cost))
            row1 = row2
        return min(row1)

    def __call__(self, value):
        for haystack in self.haystacks:
            distance = self.fuzzy_substring(value, haystack)
            longest = max(len(value), len(haystack))
            similarity = (longest - distance) / longest
            if similarity >= self.__password_match_threshold:
                raise ValidationError(
                    self.message % {"haystacks": ", ".join(self.haystacks)},
                    code=self.code)

class DictionaryValidator(BaseSimilarityValidator):
    message = _("Based on a dictionary word.")
    code = "dictionary_word"

    def __init__(self, words=None, dictionary=None, *args, **kwargs):
        haystacks = []
        if dictionary:
            with open(dictionary) as dictionary:
                haystacks.extend(
                    [smart_unicode(x.strip()) for x in dictionary.readlines()]
                )
        if words:
            haystacks.extend(words)
        super(DictionaryValidator, self).__init__(haystacks=haystacks, *args, **kwargs)


class CommonSequenceValidator(BaseSimilarityValidator):
    message = _("Based on a common sequence of characters")
    code = "common_sequence"

