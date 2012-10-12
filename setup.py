import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = ['pyramid', 'WebError', 'mongoengine',
                'pyramid-openid', 'blinker',
            'pyramid_beaker', 'gevent-socketio',
            'gunicorn']

setup(name='lobbypy',
      version='0.0',
      description='lobbypy',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author="Mark McGuire",
      author_email='mark.b.mcg@gmail.com',
      url='https://github.com/TronPaul/lobbypy',
      keywords='tf2 web lobby',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="lobbypy.tests",
      entry_points = """\
      [paste.app_factory]
      main = lobbypy:main
      """,
      paster_plugins=['pyramid'],
      )

