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



The following tracked items are required for unit tests:

+--------------+--------------+
| Name         | Code         |
+==============+==============+
| Once Item    | ONCE_ITEM    |
+--------------+--------------+
| Monthly Item | MONTHLY_ITEM |
+--------------+--------------+

The following plan codes are required for unit tests:

+-----------------+-----------------+---------+-----------+--------------+
| Plan Name       | Code            | Price   | ONCE_ITEM | MONTHLY_ITEM |
+=================+=================+=========+===========+==============+
| Free Monthly    | FREE_MONTHLY    | $0.00   | 1         | 10           |
+-----------------+-----------------+---------+-----------+--------------+
| Paid Monthly    | PAID_MONTHLY    | $10.00  | 1         | 10           |
+-----------------+-----------------+---------+-----------+--------------+
| Tracked Monthly | TRACKED_MONTHLY | $10.00  | 1         | 10           |
+-----------------+-----------------+---------+-----------+--------------+


The following promotions are required for unit tests:

+----------------+---------------+--------+-----------+
| Promotion Name | Coupon Code   | % Off  | Duration  |
+================+===============+========+===========+
| Coupon         | COUPON        | 10     | Forever   |
+----------------+---------------+--------+-----------+
| Coupon 2       | COUPON2       | 20     | Forever   |
+----------------+---------------+--------+-----------+

Be sure to turn on the native gateway credit card option in Configuration > Product settings > Gateway Settings.

Config
======

In the tests folder, copy the config.ini.template to config.ini. Fill in your email, password, and product code.

Running Tests
=============
Run the test with nosetests.

.. code::

    nosetests
