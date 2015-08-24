Requirements
============

Inside a virtualenv, run:

.. code::

    pip install -r dev-requirements.txt

Installing elementtree for Unit Testing
=======================================================
When trying to install elementtree, pip may report that there is no such package. If this happens to you, you can work around by downloading and installing it manually.

.. code::

    wget http://effbot.org/media/downloads/elementtree-1.2.6-20050316.zip
    unzip elementtree-1.2.6-20050316.zip
    cd elementtree-1.2.6-20050316/
    pip install .

CheddarGetter Setup
=============
You will also need to setup the correct plans in cheddar. You may want to set up a product intended just for testing.

The following plan codes are required for unit tests:

* FREE_MONTHLY
* PAID_MONTHLY

Be sure you turn on the native gateway credit card option.

Config
======

In the tests folder, copy the config.ini.template to config.ini. Fill in your email, password, and product code.

Running Tests
=============
Run the test with nosetests.

.. code::

    nosetests
