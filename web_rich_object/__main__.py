from __future__ import print_function
import sys
from . import WebRichObject

if len(sys.argv) < 2:
    print("You must specify a URL")
    sys.exit(1)
wro = WebRichObject(sys.argv[1])
print("%-15s => %s" % ('title', wro.title))
print("%-15s => %s" % ('type', wro.type))
print("%-15s => %s" % ('url', wro.url))
print("%-15s => %s" % ('image', wro.image))
sys.exit(0)
