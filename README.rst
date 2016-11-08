Web Rich Object
===============

This module aims to describe a URL as a Web Rich Object.

It firstly uses OpenGraph protocol and try to guess without.


    >>> from web_rich_object import WebRichObject
    >>> wro = WebRichObject('https://www.youtube.com/watch?v=4nzaATIOAAE')
    >>> wro.title
    'Sir Samuel - Urban Classik [CLIP OFFICIEL]'
    >>> wro.site_name
    'YouTube'
    >>> wro.image
    'https://i.ytimg.com/vi/4nzaATIOAAE/maxresdefault.jpg'
    >>> wro.url
    'https://www.youtube.com/watch?v=4nzaATIOAAE'
