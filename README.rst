scsgate |Build Status| |Docs|
=============================

This python module allows to interact with a
`SCSGate <https://goo.gl/aKnpDw>`__ device.

The module has been written to manage a SCSGate device with
`home-assistant <https://home-assistant.io/>`__.

Installation
------------

The scsgate module can be installed using pip:

::

    sudo pip install scsgate

Monitoring the SCS bus
----------------------

The scsgate pip package provides a script named ``scs-monitor`` that has
two purposes:

-  interactively create a configuration file for home-assistant
-  sniff all the messages going over the SCS bus

Creation of a home-assistant configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``scs-monitor`` can be used to create a home-assistant configuration
file defining all the available devices.

This can be done by using the ``--homeassistant-config`` flag.

Once started ``scs-monitor`` will start sniffing all the events going
over the SCS bus. For each captured message it will extract the ID of
the relevant device and will ask the user to enter an ID for
home-assistant and the name of the device.

By pressing ``CTRL-C`` the program will exit and generate the
home-assistant configuration file.

Sniffing messages
~~~~~~~~~~~~~~~~~

By defaul ``scs-monitor`` will print all the messages going over the SCS
buffer.

It's possible to filter the messages related with a list of known
devices. This can be done using the ``-f`` flag followed by the name of
the file containing the devices to ignore. The file is a yaml document
like the one created in the previous step.

It's also possible to redirect all the output to a text file by using
the ``-o`` flag.

License
~~~~~~~

This code is licensed under the MIT license.

.. |Build Status| image:: https://travis-ci.org/flavio/scsgate.svg?branch=master
   :target: https://travis-ci.org/flavio/scsgate
.. |Docs| image:: https://readthedocs.org/projects/scsgate/badge/?version=latest
   :target: http://scsgate.readthedocs.org/en/latest/?badge=latest
