from __future__ import unicode_literals

import unittest
import re
from datetime import datetime
import warnings

from web_rich_object.api import WebRichObject as WRO


TEST_URLS = [
    # Website
    ('http://example.com', {'title': 'Example Domain', 'url': 'http://example.com', 'site_name': 'example.com', 'type': 'website', 'subtype': 'html', 'image': None, 'generator': None, 'author': None, 'tags': []}),
    ('http://google.com', {'title': 'Google', 'site_name': 'google.com', 'subtype': 'html'}),
    ('http://stackoverflow.com/', {'title': 'Stack Overflow', 'url': 'http://stackoverflow.com/', 'site_name': 'stackoverflow.com', 'type': 'website', 'subtype': 'html', 'generator': None, 'author': None, 'tags': []}),
    ('https://github.com/', {'title': 'Build software better, together', 'url': 'https://github.com', 'site_name': 'GitHub', 'type': 'website', 'subtype': 'html', 'image': 'https://assets-cdn.github.com/images/modules/open_graph/github-logo.png', 'generator': None, 'author': None, 'tags': []}),
    ('https://en.wikipedia.org/wiki/Main_Page', {'title': 'Wikipedia, the free encyclopedia', 'url': 'https://en.wikipedia.org/wiki/Main_Page', 'site_name': 'en.wikipedia.org', 'type': 'website', 'subtype': 'html', 'tags': []}),
    ('https://en.wikipedia.org/wiki/', {'title': 'Wikipedia, the free encyclopedia', 'url': 'https://en.wikipedia.org/wiki/', 'site_name': 'en.wikipedia.org', 'type': 'website', 'subtype': 'html', 'tags': []}),
    ('https://en.wikipedia.org/wiki/Portugal', {'title': 'Portugal - Wikipedia', 'url': 'https://en.wikipedia.org/wiki/Portugal', 'site_name': 'en.wikipedia.org', 'type': 'website', 'subtype': 'html', 'tags': []}),
    ('https://www.revealnews.org/article/uber-said-it-protects-you-from-spying-security-sources-say-otherwise/', {'title': "Uber said it protects you from spying. Security sources say otherwise", 'url': 'https://www.revealnews.org/article/uber-said-it-protects-you-from-spying-security-sources-say-otherwise/', 'site_name': 'Reveal', 'type': 'article', 'subtype': 'html', 'tags': ['privacy', 'surveillance', 'uber'], 'category': None, 'published_time': datetime(2016, 12, 12, 8, 0, 15), 'modified_time': datetime(2016, 12, 12, 23, 40, 26)}),
    ('http://rue89.nouvelobs.com/2016/12/19/gagner-temps-ils-matent-films-series-vitesse-acceleree-265930', {'title': "Rue89", 'url': 'http://rue89.nouvelobs.com/2016/12/19/gagner-temps-ils-matent-films-series-vitesse-acceleree-265930', 'site_name': 'Rue89', 'type': 'website', 'subtype': 'html', 'tags': [], 'category': None, 'published_time': None, 'modified_time': None}),
    ('http://www.permaculturedesign.fr/pedagogie-montessori-ecole-enseigner-permaculture-design', {'title': 'Enseigner autrement avec la p\xe9dagogie Montessori.', 'url': 'http://www.permaculturedesign.fr/pedagogie-montessori-ecole-enseigner-permaculture-design', 'site_name': 'Blog du bureau d\u2019\xe9tudes PermacultureDesign', 'type': 'article', 'subtype': 'html', 'tags': [], 'category': None, 'published_time': None, 'modified_time': None}),
    # Image
    ('https://en.wikipedia.org/static/images/project-logos/enwiki-2x.png', {'title': 'en.wikipedia.org', 'url': 'https://en.wikipedia.org/static/images/project-logos/enwiki-2x.png', 'site_name': 'en.wikipedia.org', 'type': 'image', 'subtype': 'png', 'tags': []}),
    ('https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif', {'title': 'upload.wikimedia.org', 'url': 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif', 'site_name': 'upload.wikimedia.org', 'type': 'image', 'subtype': 'gif', 'tags': []}),
    ('https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_example_JPG_RIP_001.jpg', {'title': 'upload.wikimedia.org', 'url': 'https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_example_JPG_RIP_001.jpg', 'site_name': 'upload.wikimedia.org', 'type': 'image', 'subtype': 'jpeg', 'tags': []}),
    # PDF
    ('https://en.wikipedia.org/w/index.php?title=Special:Book&bookcmd=download&collection_id=c3c8c9c039141278a7153bf56abeba2c5fd3c798&writer=rdf2latex&return_to=Main+Page', {'title': 'Main Page', 'url': 'https://en.wikipedia.org/w/index.php?title=Special:Book&bookcmd=download&collection_id=c3c8c9c039141278a7153bf56abeba2c5fd3c798&writer=rdf2latex&return_to=Main+Page', 'site_name': 'en.wikipedia.org', 'type': 'application', 'subtype': 'pdf', 'tags': []}),
    ('https://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial:Livre&bookcmd=download&collection_id=796fcc2700efddffefc3584fb895f54d336fa485&writer=rdf2latex&return_to=Ch%C3%AAne', {'title': 'Ch\xeane', 'url': 'https://fr.wikipedia.org/w/index.php?title=Sp%C3%A9cial:Livre&bookcmd=download&collection_id=796fcc2700efddffefc3584fb895f54d336fa485&writer=rdf2latex&return_to=Ch%C3%AAne', 'site_name': 'fr.wikipedia.org', 'type': 'application', 'subtype': 'pdf', 'tags': []}),
    ('https://ar.wikipedia.org/w/index.php?title=%D8%AE%D8%A7%D8%B5:%D9%83%D8%AA%D8%A7%D8%A8&bookcmd=download&collection_id=272731759933b793795ade084d0fbbfaca4ea054&writer=rdf2latex&return_to=%D8%A7%D9%84%D8%B5%D9%81%D8%AD%D8%A9+%D8%A7%D9%84%D8%B1%D8%A6%D9%8A%D8%B3%D9%8A%D8%A9', {'title': '\u0627\u0644\u0635\u0641\u062d\u0629 \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629', 'url': 'https://ar.wikipedia.org/w/index.php?title=%D8%AE%D8%A7%D8%B5:%D9%83%D8%AA%D8%A7%D8%A8&bookcmd=download&collection_id=272731759933b793795ade084d0fbbfaca4ea054&writer=rdf2latex&return_to=%D8%A7%D9%84%D8%B5%D9%81%D8%AD%D8%A9+%D8%A7%D9%84%D8%B1%D8%A6%D9%8A%D8%B3%D9%8A%D8%A9', 'site_name': 'ar.wikipedia.org', 'type': 'application', 'subtype': 'pdf', 'tags': []}),
    # Video
    ('https://www.youtube.com/watch?v=4nzaATIOAAE', {'title': 'Sir Samuel - Urban Classik [CLIP OFFICIEL]', 'url': 'https://www.youtube.com/watch?v=4nzaATIOAAE', 'site_name': 'YouTube', 'type': 'video', 'subtype': 'html', 'image': 'https://i.ytimg.com/vi/4nzaATIOAAE/maxresdefault.jpg', 'generator': None, 'author': None, 'tags': []}),
    ('http://www.dailymotion.com/video/x2h2pgt_yannick-van-doorne-l-electroculture-une-technologie-d-avenir-meta-tv-1-4_tv', {'title': "Yannick Van Doorne - L'\xe9lectroculture une technologie d'avenir - Meta TV 3/4 - vid\xe9o Dailymotion", 'url': 'http://www.dailymotion.com/video/x2h2pgt', 'site_name': 'Dailymotion', 'type': 'video', 'subtype': 'html', 'image': 'http://s1.dmcdn.net/I8M_O/526x297-FRU.jpg', 'generator': None, 'author': None, 'tags': []}),
]

NOT_ALPHA_REG = re.compile(r'[^A-Za-z]')
UNDERSCORE_REG = re.compile(r'_+')


def gen_test(url, wro_attrs):
    def func(self):
        wro = WRO(url)
        attrs = {k: getattr(wro, k) for k, v in wro_attrs.iteritems()}
        expected_attrs = {k: v for k, v in wro_attrs.iteritems()}
        self.assertEqual(attrs, expected_attrs)
    return func


class MetaFunctionalTest(type):
    def __new__(mcls, name, bases, attrs):
        for url, wro_attrs in TEST_URLS:
            func_name = 'test_' + NOT_ALPHA_REG.sub('_', url)
            func_name = UNDERSCORE_REG.sub('_', func_name)[:100]
            func = gen_test(url, wro_attrs)
            if func_name in attrs:
                warnings.warn('%s already set' % func_name)
            attrs[func_name] = func
        return type.__new__(mcls, name, bases, attrs)


class FunctionalTest(unittest.TestCase):
    __metaclass__ = MetaFunctionalTest
    maxDiff = None


if __name__ == '__main__':
    unittest.main()
