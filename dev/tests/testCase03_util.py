#coding=utf-8
import unittest
import sys
sys.path.insert(0,'..')

import scriptcontext as sc
import caad.utility as util

import caad
reload(caad.utility)

class TestCase03(unittest.TestCase):
    def testUrl(self):
        url = "https://jsonplaceholder.typicode.com/posts/"
        lines = util.getContentFromUrl(url)
        util.openUrl(url)
        for line in lines:
            print line


