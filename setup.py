from setuptools import setup, find_packages
import web_rich_object


def read_file(name):
    with open(name) as fd:
        return fd.read()

setup(
    name="web-rich-object",
    version=web_rich_object.__version__,
    author=web_rich_object.__author__,
    author_email=web_rich_object.__email__,
    description=web_rich_object.__doc__,
    url=web_rich_object.__url__,
    keywords=web_rich_object.__keywords__,
    license=web_rich_object.__license__,
    py_modules=['web_rich_object'],
    packages=find_packages(),
    install_requires=read_file('requirements.txt').splitlines(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=read_file('README.rst')
)
