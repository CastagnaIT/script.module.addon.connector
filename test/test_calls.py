# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
from AddonSignals import _jsonrpc, makeCall, registerCall, returnCall

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.sender.id'


def callback(data):
    xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback.data = data


class TestCalls(unittest.TestCase):

    def test_calls(self):
        data = dict(test='signals')
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        returnCall('test_signal', data=data)
        self.assertEqual(data, callback.data)
        makeCall(signal='test_signal', data=data, source_id='plugin.sender.id')
        self.assertEqual(data, callback.data)

    def test_unicode(self):
        data = dict(test='unicode', string='Föóbàr')
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        returnCall('test_signal', data=data)
        self.assertEqual(data, callback.data)
        makeCall(signal='test_signal', data=data, source_id='plugin.sender.id')
        self.assertEqual(data, callback.data)

    def test_bogus_sender(self):
        data = dict(test='bogus_sender')
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        returnCall('test_signal', data=data)
        returnCall('test_signal', data=dict(bogus='data'), source_id='bogus.sender.id')
        self.assertEqual(data, callback.data)
        makeCall(signal='test_signal', data=data, source_id='plugin.sender.id')
        self.assertEqual(data, callback.data)

    def test_send_multiple(self):
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        for idx in range(3):
            returnCall('test_signal', data=dict(test='send_multiple', idx=idx))
        self.assertEqual(dict(test='send_multiple', idx=2), callback.data)

    @staticmethod
    def test_register_multiple():
        data = dict(test='register_multiple')
        registerCall('plugin.sender.id', signal='test_signal', callback=print)
        registerCall('plugin.sender.id', signal='test_signal', callback=xbmc.log)  # Debug
        returnCall('test_signal', data=data, source_id='plugin.sender.id')
        makeCall(signal='test_signal', data=data, source_id='plugin.sender.id')

    @staticmethod
    def test_unregister_nonexisting():
        data = dict(test='unregister_nonexisting')
        makeCall(signal='test_foo', source_id='bogus.sender.id', data=data)
        makeCall(signal='test_foo', source_id='plugin.sender.id', data=data)
        makeCall(signal='test_bar', source_id='plugin.sender.id', data=data)

    def test_send_unregistered(self):
        data = dict(test='send_unregistered')
        returnCall('test_signal', data=data)
        self.assertEqual(data, callback.data)

    def test_send_nonsignal(self):
        data = dict(test='send_nonsignal')
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        returnCall('test_signal', data=data)
        _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id',
            message='test_nonsignal',
            data=dict(bogus='data'),
        ))
        self.assertEqual(data, callback.data)

    def test_send_none(self):
        data = dict(test='send_none')
        registerCall('plugin.sender.id', signal='test_signal', callback=callback)
        returnCall('test_signal', data=data)
        _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id',
            message='test_nonsignal',
            data=None,
        ))
        self.assertEqual(data, callback.data)
