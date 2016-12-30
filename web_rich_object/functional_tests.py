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
    ('https://en.wikipedia.org/static/images/project-logos/enwiki-2x.png', {'title': 'enwiki-2x.png', 'url': 'https://en.wikipedia.org/static/images/project-logos/enwiki-2x.png', 'site_name': 'en.wikipedia.org', 'type': 'image', 'subtype': 'png', 'tags': []}),
    ('https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif', {'title': 'Rotating_earth_(large).gif', 'url': 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Rotating_earth_%28large%29.gif', 'site_name': 'upload.wikimedia.org', 'type': 'image', 'subtype': 'gif', 'tags': []}),
    ('https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_example_JPG_RIP_001.jpg', {'title': 'JPEG_example_JPG_RIP_001.jpg', 'url': 'https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_example_JPG_RIP_001.jpg', 'site_name': 'upload.wikimedia.org', 'type': 'image', 'subtype': 'jpeg', 'tags': []}),
    # PDF
    ('http://www.sample-videos.com/pdf/Sample-pdf-5mb.pdf', {'title': 'Sample-pdf-5mb.pdf', 'url': 'http://www.sample-videos.com/pdf/Sample-pdf-5mb.pdf', 'site_name': 'www.sample-videos.com', 'type': 'application', 'subtype': 'pdf', 'tags': []}),
    ('http://www.pdf995.com/samples/pdf.pdf', {'title': 'PDF', 'url': 'http://www.pdf995.com/samples/pdf.pdf', 'site_name': 'www.pdf995.com', 'type': 'application', 'subtype': 'pdf', 'tags': ['pdf,', 'create', 'pdf,', 'software,', 'acrobat,', 'adobe']}),
    # ('http://www.cbu.edu.zm/downloads/pdf-sample.pdf', {'title': 'This is a test PDF file', 'url': 'http://www.cbu.edu.zm/downloads/pdf-sample.pdf', 'site_name': 'www.cbu.edu.zm', 'type': 'application', 'subtype': 'pdf', 'tags': []}),
    # Video HTML
    ('https://www.youtube.com/watch?v=4nzaATIOAAE', {'title': 'Sir Samuel - Urban Classik [CLIP OFFICIEL]', 'url': 'https://www.youtube.com/watch?v=4nzaATIOAAE', 'site_name': 'YouTube', 'type': 'video', 'subtype': 'html', 'image': 'https://i.ytimg.com/vi/4nzaATIOAAE/maxresdefault.jpg', 'generator': None, 'author': None, 'tags': ['sir', 'samuel', 'teaser', 'gallery', 'miroir', 'aime', 'casquette', 'reggae', 'ragga', 'dub', 'hip', 'hop', 'rap', 'saian', 'supa', 'crew', 'fefe', 'mental', 'offishall', 'secher', 'larmes', 'urban', '...'], 'video': 'https://www.youtube.com/embed/4nzaATIOAAE'}),
    ('http://www.dailymotion.com/video/x2h2pgt_yannick-van-doorne-l-electroculture-une-technologie-d-avenir-meta-tv-1-4_tv', {'title': "Yannick Van Doorne - L'\xe9lectroculture une technologie d'avenir - Meta TV 3/4 - vid\xe9o Dailymotion", 'url': 'http://www.dailymotion.com/video/x2h2pgt', 'site_name': 'Dailymotion', 'type': 'video', 'subtype': 'html', 'image': 'http://s1.dmcdn.net/I8M_O/526x297-FRU.jpg', 'generator': None, 'author': None, 'tags': ['Agriculture'], 'video': 'http://www.dailymotion.com/embed/video/x2h2pgt?autoplay=1'}),

    ('http://www.koreus.com/video/faux-professeur-chimie.html', {'title': 'Un faux professeur le premier jour de cours (Blague)', 'url': 'http://www.koreus.com/video/faux-professeur-chimie.html', 'type': 'video.other', 'subtype': 'html', 'image': 'http://thumbshigh.koreus.com/201309/faux-professeur-chimie.jpg', 'generator': None, 'author': None, 'tags': ['uid Vid\xe9o', 'amphi', 'blague', 'chimie', 'cours', 'faux', 'professeur', 'vostfr', 'clip', 'fun', 'jeu', 'divertissement', 'loisir', 'humour', 'animation', 'gratuit'], 'video': 'http://www.koreus.com/video/faux-professeur-chimie/autostart', 'video_width': '1280', 'video_height': '720'}),
    # ('https://vimeo.com/39075039', {'title': 'Nike SB: Eric Koston - Mr. Control It All', 'url': 'https://vimeo.com/39075039', 'type': 'video', 'subtype': 'html', 'image': 'https://i.vimeocdn.com/video/269350328_1280x720.jpg', 'generator': None, 'author': None, 'tags': ['Nike', 'Nike SB', 'Nike Skateboarding', 'skate', 'skateboard', 'skateboarding', 'Koston', 'Eric Koston', 'Malto', 'Sean Malto', 'Justin Brock', 'Mr. Control It All'], 'video': 'https://player.vimeo.com/video/39075039?autoplay=1'}),
    # Page with HTML5 video
    ('http://www.w3schools.com/html/html5_video.asp', {'title': "HTML5 Video", 'url': 'http://www.w3schools.com/html/html5_video.asp', 'type': 'website', 'subtype': 'html', 'image': 'http://www.w3schools.com/favicon.ico', 'generator': None, 'author': None, 'tags': [], 'video': 'http://www.w3schools.com/html/mov_bbb.mp4'}),
    # Video files
    ('http://www.sample-videos.com/video/mp4/240/big_buck_bunny_240p_1mb.mp4', {'title': 'big_buck_bunny_240p_1mb.mp4', 'url': 'http://www.sample-videos.com/video/mp4/240/big_buck_bunny_240p_1mb.mp4', 'type': 'video', 'subtype': 'mp4', 'image': None, 'generator': None, 'author': None, 'tags': [], 'video': 'http://www.sample-videos.com/video/mp4/240/big_buck_bunny_240p_1mb.mp4'}),
    ('http://www.sample-videos.com/video/flv/240/big_buck_bunny_240p_1mb.flv', {'title': 'big_buck_bunny_240p_1mb.flv', 'url': 'http://www.sample-videos.com/video/flv/240/big_buck_bunny_240p_1mb.flv', 'type': 'video', 'subtype': 'x-flv', 'image': None, 'generator': None, 'author': None, 'tags': [], 'video': 'http://www.sample-videos.com/video/flv/240/big_buck_bunny_240p_1mb.flv'}),
    ('http://www.sample-videos.com/video/mkv/240/big_buck_bunny_240p_1mb.mkv', {'title': 'big_buck_bunny_240p_1mb.mkv', 'url': 'http://www.sample-videos.com/video/mkv/240/big_buck_bunny_240p_1mb.mkv', 'type': 'video', 'subtype': 'x-matroska', 'image': None, 'generator': None, 'author': None, 'tags': [], 'video': 'http://www.sample-videos.com/video/mkv/240/big_buck_bunny_240p_1mb.mkv'}),
    ('http://www.sample-videos.com/video/3gp/240/big_buck_bunny_240p_1mb.3gp', {'title': 'big_buck_bunny_240p_1mb.3gp', 'url': 'http://www.sample-videos.com/video/3gp/240/big_buck_bunny_240p_1mb.3gp', 'type': 'video', 'subtype': '3gpp', 'image': None, 'generator': None, 'author': None, 'tags': [], 'video': 'http://www.sample-videos.com/video/3gp/240/big_buck_bunny_240p_1mb.3gp'}),
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
