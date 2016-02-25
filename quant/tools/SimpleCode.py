# -*- coding: UTF-8 -*-
import chardet


class SimpleCode:
    """A class for detecting the encoding of a *ML document and
    converting it to a Unicode string. If the error, try to encode
    with utf-8"""

    def __init__(self, data):
        self.originalData = data
        self.originalEncoding = None
        self.unicodeData = self.tryConvert()

    def __str__(self):
        return self.unicodeData

    def tryConvert(self):
        try:
            encoding = self.detect(self.originalData)
            #not luck, use chartset
            if not encoding:
                encoding = chardet.detect(self.originalData)['encoding']
            if not encoding:
                print "Get encoding false, set utf-8 default"
                encoding = "utf-8"

            self.originalEncoding = encoding
            return self.toUnicode(self.originalData, encoding)
        except:
            #traceback.print_exc()
            self.originalEncoding = None
            return ""

    def toUnicode(self, data, encoding):
        '''Given a string and its encoding, decodes the string into Unicode.
        %encoding is a string recognized by encodings.aliases'''
        # strip Byte Order Mark (if present)
        if (len(data) >= 4) and (data[:2] == '\xfe\xff') and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16be'
            data = data[2:]
        elif (len(data) >= 4) and (data[:2] == '\xff\xfe') and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16le'
            data = data[2:]
        elif data[:3] == '\xef\xbb\xbf':
            encoding = 'utf-8'
            data = data[3:]
        elif data[:4] == '\x00\x00\xfe\xff':
            encoding = 'utf-32be'
            data = data[4:]
        elif data[:4] == '\xff\xfe\x00\x00':
            encoding = 'utf-32le'
            data = data[4:]
        newdata = unicode(data, encoding, errors='replace')
        return newdata

    def detect(self, line, num=450):
        try:
            l = len(line)
            if l < 1200:
                return chardet.detect(line)['encoding']
            else:
                #first
                res1 = chardet.detect(line[: num])
                #second
                str2 = line[l/2: l/2 + num]
                start = str2.find(' ')
                if start == -1:
                    start = 0
                res2 = chardet.detect(str2[start:])
                if res1['encoding'] != res2['encoding']:
                    if res1['encoding'] == 'ascii':
                        return res2['encoding']
                    else:
                        str3 = line[l/3: l/3 + num]
                        start = str2.find(' ')
                        if start == -1:
                            start = 0
                        #third
                        res3 = chardet.detect(str3[start:])
                        if res3['encoding'] == res2['encoding']:
                            return res2['encoding']
                        else:
                            return res1['encoding']
                else:
                    return res1['encoding']
        except:
            print "detect error, return None"
            return None
