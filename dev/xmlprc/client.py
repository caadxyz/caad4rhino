#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://cewing.github.io/training.codefellows/assignments/day12/xmlrpc.html
# https://pymotw.com/3/xmlrpc.client/
import xmlrpclib
proxy = xmlrpclib.ServerProxy('http://localhost:50000', verbose=True)
proxy.multiply(3, 24)
