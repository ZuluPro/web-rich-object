import faker
import factory
from factory import fuzzy
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

FILE_EXTS = faker.providers.file.Provider.file_extensions

WRO_TYPES = (
    'article',
    'website',
    'video',
    'image',
    'application',
    'text',
    'audio',
)
WRO_SUBTYPES = {
    'article': ('html',),
    'website': ('html',),
    'video': ('html',) + FILE_EXTS['video'],
    'image': ('html',) + FILE_EXTS['image'],
    'application': ('pdf',),
    'text': FILE_EXTS['text'],
    'audio': ('html',) + FILE_EXTS['audio'],
}


def lazy_subtype(wro):
    if wro.type not in WRO_SUBTYPES:
        return 'website'
    subtypes = WRO_SUBTYPES[wro.type]
    return fuzzy.FuzzyChoice(subtypes).fuzz()


class MockWebRichObject(MagicMock):
    pass


class WebRichObjectFactory(factory.Factory):
    title = factory.Faker('sentence')
    type = fuzzy.FuzzyChoice(WRO_TYPES)
    subtype = factory.LazyAttribute(lazy_subtype)

    image = factory.Faker('image_url')
    base_url = factory.Faker('uri')
    url = factory.LazyAttribute(lambda w: w.base_url)
    video = factory.Faker('url')
    audio = factory.Faker('url')

    site_name = factory.Faker('company')
    description = factory.Faker('sentence', nb_words=25)
    site_name = factory.Faker('name')
    author = factory.Faker('name')

    created_time = factory.Faker('date_time_between', start_date='-30d', end_date='-20d')
    published_time = factory.Faker('date_time_between', start_date='-20d', end_date='-10d')
    modified_time = factory.Faker('date_time_between', start_date='-10d', end_date='now')
    expiration_time = factory.Faker('date_time_between', start_date='now', end_date='+10d')

    generator = factory.Faker('company')
    determiner = fuzzy.FuzzyChoice(['a', 'an', 'auto', None])
    locale = factory.Faker('language_code')
    locale_alternative = []

    section = factory.Faker('word')
    tags = factory.Faker('words')

    class Meta:
        model = MockWebRichObject
