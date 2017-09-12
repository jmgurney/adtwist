#!/usr/bin/env python

from alarmdecoder.event import event

from twisted.internet import reactor  
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.protocols import basic
from twisted.test import proto_helpers
from twisted.trial import unittest 

import alarmdecoder
import mock
import twisted.internet.serialport 

__all__ = [ 'AlarmDecoderProtocol', 'adtwist' ]

class AlarmDecoderProtocol(basic.LineReceiver):
	'''This is a twisted protocol for AlarmDecoder.

	To use this class, instantiate the class.  Then you must pass it to
	AlarmDecoder as it's device and pass it to the transport.  Once both
	calls have been made, only a reference to the AlarmDecoder instance
	should be kept.

	There is a helper function adtwist that does this work with a SerialPort
	transport.
	'''

	# Protocol Stuff
	delimiter = '\r\n'

	def lineReceived(self, line):
		self.on_read(data=line)

	# AD Device Stuff
	on_open = event.Event("This event is called when the device has been opened.\n\n**Callback definition:** *def callback(device)*")
	on_close = event.Event("This event is called when the device has been closed.\n\n**Callback definition:** def callback(device)*")
	on_read = event.Event("This event is called when a line has been read from the device.\n\n**Callback definition:** def callback(device, data)*")
	on_write = event.Event("This event is called when data has been written to the device.\n\n**Callback definition:** def callback(device, data)*")

	def open(self, baudrate=None, no_reader_thread=None):
		# We don't have anything to do on open.  We might want to
		# possibly do the transport connection here, or verify that
		# we have a transport.

		self.on_open()
		return self

	def write(self, data):
		self.transport.write(data)
		self.on_write(data=data)

	def close(self):
		self.on_close()

def adtwist(serdev, *args, **kwargs):
	'''Create an AlarmDecoder instance using the twisted SerialPort transport.

	The arguments that are passed to this function are passed to SerialPort
	allowing the setting of SerialPort's parameters.

	open will have already been called.
	'''

	adp = AlarmDecoderProtocol()
	ad = alarmdecoder.AlarmDecoder(adp)

	twisted.internet.serialport.SerialPort(adp, serdev, reactor, *args, **kwargs)

	ad.open()

	return ad

class TestADProtocol(unittest.TestCase):
	@staticmethod
	def getTimeout():
		return .2

	def setUp(self):
		self.adp = AlarmDecoderProtocol()
		self.ad = alarmdecoder.AlarmDecoder(self.adp)
		self.tr = proto_helpers.StringTransport()
		self.adp.makeConnection(self.tr)

		openmock = mock.MagicMock()
		self.adp.on_open += openmock

		self.ad.open()

		openmock.assert_called_once_with(self.adp)

		self.assertEqual(self.tr.value(), 'C\rV\r')
		self.tr.clear()

		self.adp.dataReceived('!CONFIG>ADDRESS=18&CONFIGBITS=ff00&LRR=N&EXP=NNNNN&REL=NNNN&MASK=ffffffff&DEDUPLICATE=N\r\n')
		self.adp.dataReceived('!VER:ffffffff,V2.2a.6,TX;RX;SM;VZ;RF;ZX;RE;AU;3X;CG;DD;MF;LR;KE;MK;CB\r\n')

	@mock.patch('alarmdecoder.AlarmDecoder.open')
	@mock.patch('twisted.internet.serialport.SerialPort')
	def test_adtwist(self, spmock, openmock):
		dev = 'somedev'
		origkwargs = { 'baudrate': 123 }
		ret = adtwist(dev, **origkwargs)

		self.assertIsInstance(ret, alarmdecoder.AlarmDecoder)

		args, kwargs = spmock.call_args
		self.assertIsInstance(args[0], AlarmDecoderProtocol)
		self.assertEqual(args[1], dev)
		self.assertEqual(kwargs, origkwargs)

		openmock.assert_called_once()

	def test_close(self):
		closemock = mock.MagicMock()
		self.adp.on_close += closemock

		self.ad.close()

		closemock.assert_called_once_with(self.adp)

	def test_adprot(self):
		alarmfun = mock.MagicMock()

		ad = self.ad
		adp = self.adp

		#print `self.tr.value()`
		self.assertEqual(ad.version_number, 'V2.2a.6')

		msgmock = mock.MagicMock()

		ad.on_message += msgmock

		data = '[0000000111000100----],006,[f7000007100600202a020000000000],"FIRE 06                         "\r\n'
		msgdata = data[:-2]
		if False: # pragma: no cover
			# This'd be nice, but the Message object doesn't have a working equality operator
			from alarmdecoder.messages import Message
			dmsg = Message(msgdata)

		readmock = mock.MagicMock()
		readmockad = mock.MagicMock()
		adp.on_read += readmock
		ad.on_read += readmockad
		adp.dataReceived(data)
		readmock.assert_called_once_with(adp, data=msgdata)
		readmockad.assert_called_once_with(ad, data=msgdata)

		msgmock.assert_called_once()
		msg = msgmock.call_args[1]['message']
		self.assertTrue(msg.ac_power)
		self.assertEqual(msg.text, 'FIRE 06                         ')
		msgmock.reset_mock()

		adp.dataReceived('[0000000110000000----],010,[f70000071010000028020000000000],"FAULT 10                        "\r\n')

		msgmock.assert_called_once()
		msg = msgmock.call_args[1]['message']
		self.assertEqual(msg.text, 'FAULT 10                        ')

		writemock = mock.MagicMock()

		adp.on_write += writemock

		ad.send('5')

		self.assertEqual(self.tr.value(), '5')
		writemock.assert_called_once_with(adp, data='5')
