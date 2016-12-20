"""Web rich object handler"""
try:
    from .api import WebRichObject
except ImportError:
    pass

VERSION = (0, 2, 1)
__version__ = '.'.join([str(i) for i in VERSION])
__author__ = 'Anthony Monthe (ZuluPro)'
__email__ = 'anthony.monthe@gmail.com'
__url__ = 'https://github.com/ZuluPro/web-rich-object'
