import re
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
from PIL import Image
from django.utils.six import BytesIO

FLOAT_REG = re.compile(r'([\d\.]*).*')


def get_style(tag, style):
    for style_line in tag.attrs.get('style', '').split(';'):
        if not style_line.strip():
            continue
        key, value = style_line.split(':')
        key, value = key.strip(), value.strip()
        if key == style:
            return value


def get_attr_or_style(tag, attr):
    value = tag.attrs.get(attr)
    if not value:
        value = get_style(tag, attr)
    return value


def get_biggest_image(images):
    biggest = (None, 0)
    unknown = []
    for img in images:
        height = get_attr_or_style(img, 'height')
        if not height:
            unknown.append((img, None))
            continue
        # Hasardous computing from %
        if '%' in height:
            height = int(FLOAT_REG.sub(height, r'\1'))
            if height < 10:
                continue
            height = 1280 * height / 100
        else:
            height = int(FLOAT_REG.sub(height, r'\1'))
        # Skip too small
        if height < 50:
            continue
        if height > biggest[1]:
            biggest = (img, height)
    if biggest[0] is None and unknown:
        biggest = unknown[0]
    return biggest[0]


def get_biggest_image(urls):
    biggest = (None, 0)
    unknown = []
    for url in urls:
        try:
            image = Image.open(BytesIO(urlopen(url).read()))
        except:
            continue
        width, height = image.size
        # Skip too small
        if height < 80 or width < 80:
            continue
        if height > biggest[1]:
            biggest = (url, height)
    if biggest[0] is None and unknown:
        biggest = unknown[0]
    return biggest[0]
