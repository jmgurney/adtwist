adtwist
=======

This is a wrapper around the python module
[alarmdecoder](https://github.com/nutechsoftware/alarmdecoder) that
makes it compatible w/ the twisted framework.  This replaces the
included device so that you don't have to use a thread to handle I/O
from the device.

Currently it is only tested w/ a AD2USB via a serial port.  There is
no USB auto detect code included.


Sample Usage
------------

Sample code:
```
from adtwist import adtwist
from twisted.internet import reactor

def msgcbfun(ad, message):
	print 'received msg:', `message`

ad = adtwist('/dev/ttyU1', baudrate=115200)
ad.on_message += msgcbfun

reactor.run()
```

This will create an AlarmDecoder instance (from alarmdecoder) and attach
it to the device `/dev/ttyU1`.  It will print each message received from
the device.
