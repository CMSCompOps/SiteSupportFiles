#!/usr/bin/env python26


outf = open('/tmp/out','w')
outf.write(u'\u00B1\n'.encode('utf8'))
outf.close()
