#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Producing and Consuming XML-RPC in Python 
# https://cewing.github.io/training.codefellows/assignments/day12/xmlrpc.html
# https://pymotw.com/3/xmlrpc.client/
from SimpleXMLRPCServer import SimpleXMLRPCServer

address = ('localhost', 50000)
server = SimpleXMLRPCServer(address)

def multiply(a, b):
    """return the product of two numbers"""
    return a * b
server.register_function(multiply)

if __name__ == '__main__':
    try:
        print "Server running on %s:%s" % address
        print "Use Ctrl-C to Exit"
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print "Exiting"
