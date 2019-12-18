# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
from AddonSignals import _receiver, makeCall, registerCall, returnCall

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.sender.id'


def callback_calls(data):
    # xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback_calls.data = data
    returnCall('test_calls', data=dict(value='return_calls', data=data))


def callback_unicode(data):
    # xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback_unicode.data = data
    returnCall('test_unicode', data=dict(value='return_unicode', data=data))


def callback_bogus_sender(data):
    # xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback_bogus_sender.data = data
    returnCall('test_bogus_sender', data=dict(value='return_bogus_sender', data=data))


def callback_send_multiple(data):
    # xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback_send_multiple.data = data
    returnCall('test_send_multiple', data=dict(value='return_send_multiple', data=data))


class TestCalls(unittest.TestCase):
    registerCall('plugin.sender.id', signal='test_calls', callback=callback_calls)
    registerCall('plugin.sender.id', signal='test_unicode', callback=callback_unicode)
    registerCall('plugin.sender.id', signal='test_bogus_sender', callback=callback_bogus_sender)
    registerCall('plugin.sender.id', signal='test_send_multiple', callback=callback_send_multiple)
    old_receiver = _receiver()  # Ensure the old SignalReceiver instance is not garbage-collected
    del _receiver.cached  # Ensure we have a different SignalReceiver instance for the sender

    def test_calls(self):
        data = dict(test='calls')
        ret = makeCall(signal='test_calls', data=data, source_id='plugin.sender.id')
        self.assertEqual(data, callback_calls.data)
        self.assertEqual(ret, dict(value='return_calls', data=data))

    def test_unicode(self):
        data = dict(test='unicode', string='Föóbàr')
        ret = makeCall(signal='test_unicode', data=data, source_id='plugin.sender.id')
        self.assertEqual(data, callback_unicode.data)
        self.assertEqual(ret, dict(value='return_unicode', data=data))

    def test_bogus_sender(self):
        ret = makeCall(signal='test_bogus_sender', data=dict(bogus='data'), source_id='bogus.sender.id')
#        self.assertNotEqual(data, callback_bogus_sender.data)
        self.assertEqual(ret, None)

    def test_send_multiple(self):
        for idx in range(3):
            ret = makeCall(signal='test_send_multiple', data=dict(idx=idx), source_id='plugin.sender.id')
            self.assertEqual(dict(idx=idx), callback_send_multiple.data)
            self.assertEqual(ret, dict(value='return_send_multiple', data=dict(idx=idx)))
