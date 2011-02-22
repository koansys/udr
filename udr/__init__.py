import math
import codecs
import csv

ENCODINGS = ('utf8', 'cp1252', 'latin1', 'ascii', 'utf16')


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeDictReader:
    """
    A CSV Dict reader which will iterate over lines in the CSV file "f",
    which is encoded in the given or guessed if not given encoding.
    """
    def __init__(self, f,
                 dialect=csv.excel,
                 encoding=None,
                 fieldnames=None,
                 restkey=None,
                 restval=None,
                 **kwds):
        self.encoding = encoding if encoding else guess_encoding(f.read())
        f.seek(0)
        f = UTF8Recoder(f, self.encoding)
        self._fieldnames = fieldnames
        self.line_num = 0
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.restkey = restkey
        self.restval = restval

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = [unicode(s.strip(), "utf-8") for s in self.reader.next()]
            except StopIteration: # pragma: no cover
                pass
            except csv.Error as e: # PRAGMA: no cover
                raise InvalidHeaderFields(e) #what is a bad fieldname?
        self.line_num = self.reader.line_num
        return self._fieldnames

    fieldnames = fieldnames #pyflakes ignore redef below
    @fieldnames.setter
    def fieldnames(self, value): # PRAGMA: no cover
        self._fieldnames = [unicode(s.strip(), "utf-8") for s in value]

    def next(self):
        if self.line_num == 0:
            self.fieldnames # remove the first row if fieldnames was given
        row = [unicode(s, "utf-8") for s in self.reader.next()]
        self.line_num = self.reader.line_num
        while row == []:
            row = [unicode(s, "utf-8") for s in self.reader.next()]
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d

    def __iter__(self):
        return self


def guess_encoding(data, encodings=ENCODINGS):
    for encoding in encodings:
        try:
            data.decode(encoding)
            return encoding
        except UnicodeDecodeError: # pragma: no cover
            pass # try the next one
    return None # pragma: no cover


class InvalidHeaderFields(Exception): # PRAGMA: no cover
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "{0}: invalid keys/column names".format(self.value)
