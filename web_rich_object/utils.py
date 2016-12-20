import re
from datetime import datetime, timedelta
from io import BytesIO
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
from PIL import Image

UTC_OFFSET_REG = re.compile(r'.*([+-]\d\d).*')


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


def parse_pdf_time(date_str):
    try:
        date = datetime.strptime(date_str[2:-7], '%Y%m%d%H%M%S')
        offset = int(UTC_OFFSET_REG.sub(r'\1', date_str))
        utc_offset = timedelta(seconds=offset*3600)
        return date + utc_offset
    except ValueError:
        return None


def parse_opengraph_time(date_str):
    try:
        try:
            date = datetime.strptime(date_str[:-6], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            date = datetime.strptime(date_str[:-6].strip(), '%d/%m/%Y %H:%M:%S')
        offset = int(UTC_OFFSET_REG.sub(r'\1', date_str))
        utc_offset = timedelta(seconds=offset*3600)
        return date + utc_offset
    except (ValueError, NameError):
        return None


def parse_contextly_time(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date
    except ValueError:
        return None
