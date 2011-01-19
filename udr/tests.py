import os
import tempfile
import unittest

import udr

class TestDictFields(unittest.TestCase):
    ### "long" means the row is longer than the number of fieldnames
    ### "short" means there are fewer elements in the row than fieldnames
    def test_read_dict_fields(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("1,2,abc\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                             fieldnames=["f1", "f2", "f3"])
            self.assertEqual(reader.next(), {"f1": '1', "f2": '2', "f3": 'abc'})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_dict_no_fieldnames(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("f1,f2,f3\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj)
            self.assertEqual(reader.fieldnames, ["f1", "f2", "f3"])
            self.assertEqual(reader.next(), {"f1": '1', "f2": '2', "f3": 'abc'})
        finally:
            fileobj.close()
            os.unlink(name)

    # Two test cases to make sure existing ways of implicitly setting
    # fieldnames continue to work.  Both arise from discussion in issue3436.
    def test_read_dict_fieldnames_from_file(self):
        fd, name = tempfile.mkstemp()
        f = os.fdopen(fd, "w+b")
        try:
            f.write("f1,f2,f3\r\n1,2,abc\r\n")
            f.seek(0)
            reader = udr.UnicodeDictReader(f)
            self.assertEqual(reader.fieldnames, [u"f1", u"f2", u"f3"])
            self.assertEqual(reader.next(), {u"f1": u'1', u"f2": u'2', u"f3": u'abc'})
        finally:
            f.close()
            os.unlink(name)

    def test_read_dict_fieldnames_chain(self):
        import itertools
        fd, name = tempfile.mkstemp()
        f = os.fdopen(fd, "w+b")
        try:
            f.write("f1,f2,f3\r\n1,2,abc\r\n")
            f.seek(0)
            reader = udr.UnicodeDictReader(f)
            first = next(reader)
            for row in itertools.chain([first], reader):
                self.assertEqual(reader.fieldnames, [u"f1", u"f2", u"f3"])
                self.assertEqual(row, {u"f1": u'1', u"f2": u'2', u"f3": u'abc'})
        finally:
            f.close()
            os.unlink(name)

    def test_read_long(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                    fieldnames=["f1", "f2"])
            self.assertEqual(reader.next(), {"f1": '1', "f2": '2',
                                             None: ["abc", "4", "5", "6"]})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_long_with_rest(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                    fieldnames=["f1", "f2"], restkey="_rest")
            self.assertEqual(reader.next(), {"f1": '1', "f2": '2',
                                             "_rest": ["abc", "4", "5", "6"]})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_long_with_rest_no_fieldnames(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("f1,f2\r\n1,2,abc,4,5,6\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj, restkey="_rest")
            self.assertEqual(reader.fieldnames, ["f1", "f2"])
            self.assertEqual(reader.next(), {"f1": '1', "f2": '2',
                                             "_rest": ["abc", "4", "5", "6"]})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_short(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("1,2,abc,4,5,6\r\n1,2,abc\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                    fieldnames="1 2 3 4 5 6".split(),
                                    restval="DEFAULT")
            self.assertEqual(reader.next(), {"1": '1', "2": '2', "3": 'abc',
                                             "4": '4', "5": '5', "6": '6'})
            self.assertEqual(reader.next(), {"1": '1', "2": '2', "3": 'abc',
                                             "4": 'DEFAULT', "5": 'DEFAULT',
                                             "6": 'DEFAULT'})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_multi(self):
        sample = [
            '2147483648,43.0e12,17,abc,def\r\n',
            '147483648,43.0e2,17,abc,def\r\n',
            '47483648,43.0,170,abc,def\r\n'
            ]
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write('\r\n'.join(sample))
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                             fieldnames="i1 float i2 s1 s2".split())
            self.assertEqual(reader.next(), {"i1": '2147483648',
                                             "float": '43.0e12',
                                             "i2": '17',
                                             "s1": 'abc',
                                             "s2": 'def'})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_with_blanks(self):
        sample = ["1,2,abc,4,5,6\r\n","\r\n",
                  "1,2,abc,4,5,6\r\n"]
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write('\r\n'.join(sample))
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                             fieldnames="1 2 3 4 5 6".split())
            self.assertEqual(reader.next(), {u"1": u'1', u"2": u'2', u"3": u'abc',
                                             u"4": u'4', u"5": u'5', u"6": u'6'})
            self.assertEqual(reader.next(), {u"1": u'1', u"2": u'2', u"3": u'abc',
                                             u"4": u'4', u"5": u'5', u"6": u'6'})
        finally:
            fileobj.close()
            os.unlink(name)

    def test_read_semi_sep(self):
        fd, name = tempfile.mkstemp()
        fileobj = os.fdopen(fd, "w+b")
        try:
            fileobj.write("1;2;abc;4;5;6\r\n")
            fileobj.seek(0)
            reader = udr.UnicodeDictReader(fileobj,
                                             fieldnames="1 2 3 4 5 6".split(),
                                             delimiter=';')
            self.assertEqual(reader.next(), {u"1": u'1', u"2": u'2', u"3": u'abc',
                                             u"4": u'4', u"5": u'5', u"6": u'6'})
        finally:
            fileobj.close()
            os.unlink(name)
