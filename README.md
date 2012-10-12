lobbypy
=======

A game lobby system

lobbypy is a web based lobby system built on Pyramid and mongodb.  It's goal is to 
be as game agnostic as possible so as to allow the addition of games besides its primary focus of TF2.

Developing
----------

Prior to the steps below, make sure you have [Python 2.7](http://www.python.org/download/),
[easy\_install (aka setuptools)](http://pypi.python.org/pypi/setuptools/), and
[virtualenv](http://pypi.python.org/pypi/virtualenv/).  You will also need a
[mongodb](http://www.mongodb.org/) server and a [Steam API key](http://steamcommunity.com/dev/apikey)

1. Create a virtualenv for lobbypy:

        $virtualenv lobbypy-env

2. Clone lobbypy into your virtualenv:

        $cd lobbypy-env
        $git clone git://github.com/TronPaul/lobbypy.git

3. Run setup.py to get required packages:

        $cd lobbypy
        $../bin/python setup.py develop

4. Put your steam API key into `steam_api_key.secret`

5. Run lobbypy:

        $../bin/pserve development.ini

6. Develop!

Test Coverage
-------------

To check the current test coverage of lobbypy:

1. Get the dependencies:

        $../bin/pip install nose coverage

2. Run nosetests:

        $../bin/nosetests

   Optional add `--cover-html` arguement to generate html pages describing coverage

Developer To Do List
--------------------

See lobbypy's [Trello board](https://trello.com/b/g6qXAm1M)

Reporting Issues & Requesting Features
--------------------------------------

See lobbypy's [Issues page](https://github.com/TronPaul/lobbypy/issues)
