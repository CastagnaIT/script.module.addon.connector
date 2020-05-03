# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
from AddonSignals import _jsonrpc, registerSlot, sendSignal, unRegisterSlot

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.sender.id'


def callback(data):
    # xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback.data = data


class TestSignals(unittest.TestCase):

    def test_signals(self):
        data = dict(test='signals')
        registerSlot('plugin.sender.id', signal='test_signals', callback=callback)
        sendSignal('test_signals', data=data)
        unRegisterSlot('plugin.sender.id', signal='test_signals')
        self.assertEqual(data, callback.data)

    def test_unicode(self):
        data = dict(test='unicode', string='Föóbàr')
        registerSlot('plugin.sender.id', signal='test_unicode', callback=callback)
        sendSignal('test_unicode', data=data)
        unRegisterSlot('plugin.sender.id', signal='test_unicode')
        self.assertEqual(data, callback.data)

    def test_bogus_sender(self):
        data = dict(test='bogus_sender')
        registerSlot('plugin.sender.id', signal='test_bogus_sender', callback=callback)
        sendSignal('test_bogus_sender', data=data)
        sendSignal('test_bogus_sender', data=dict(bogus='data'), source_id='bogus.sender.id')
        unRegisterSlot('plugin.sender.id', signal='test_bogus_sender')
        self.assertEqual(data, callback.data)

    def test_send_multiple(self):
        registerSlot('plugin.sender.id', signal='test_multiple', callback=callback)
        for idx in range(3):
            sendSignal('test_multiple', data=dict(test='send_multiple', idx=idx))
        unRegisterSlot('plugin.sender.id', signal='test_multiple')
        self.assertEqual(dict(test='send_multiple', idx=2), callback.data)

    @staticmethod
    def test_register_multiple():
        data = dict(test='register_multiple')
        registerSlot('plugin.sender.id', signal='test_register_multiple', callback=print)
        registerSlot('plugin.sender.id', signal='test_register_multiple', callback=xbmc.log)  # Debug
        sendSignal('test_register_multiple', data=data, source_id='plugin.sender.id')
        unRegisterSlot('plugin.sender.id', signal='test_register_multiple')

    def test_warning(self):
        data = dict(test='warning')
        registerSlot('plugin.sender.id', signal='test_warning', callback=callback)  # Debug
        sendSignal('test_warning', data=data, sourceID='plugin.sender.id')
        unRegisterSlot('plugin.sender.id', signal='test_warning')
        self.assertEqual(data, callback.data)

    @staticmethod
    def test_unregister_nonexisting():
        unRegisterSlot('bogus.sender.id', signal='test_foo')
        unRegisterSlot('plugin.sender.id', signal='test_foo')
        unRegisterSlot('plugin.sender.id', signal='test_bar')

    def test_send_unregistered(self):
        data = dict(test='send_unregistered')
        sendSignal('test_send_unregistered', data=data)
        self.assertNotEqual(data, callback.data)

    def test_send_nonsignal(self):
        data = dict(test='send_nonsignal')
        registerSlot('plugin.sender.id', signal='test_nonsignal', callback=callback)
        sendSignal('test_nonsignal', data=data)
        _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id',
            message='test_nonsignal',
            data=dict(bogus='data'),
        ))
        unRegisterSlot('plugin.sender.id', signal='test_nonsignal')
        self.assertEqual(data, callback.data)

    def test_send_none(self):
        data = dict(test='send_none')
        registerSlot('plugin.sender.id', signal='test_send_none', callback=callback)
        sendSignal('test_send_none', data=data)
        _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id.SIGNAL',
            message='test_send_none',
            data=[],
        ))
        unRegisterSlot('plugin.sender.id', signal='test_send_none')
        self.assertEqual(None, callback.data)
