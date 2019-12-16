# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals
import unittest
import AddonSignals

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.sender.id'


def callback(data):
    xbmc.log('Received signal: %s' % data, 3)  # Warning
    callback.data = data


class TestSignals(unittest.TestCase):

    def test_signals(self):
        data = dict(test='signals')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        AddonSignals.sendSignal('test_signal', data=data)
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)

    def test_unicode(self):
        data = dict(test='unicode', string='Föóbàr')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        AddonSignals.sendSignal('test_signal', data=data)
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)

    def test_bogus_sender(self):
        data = dict(test='bogus_sender')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        AddonSignals.sendSignal('test_signal', data=data)
        AddonSignals.sendSignal('test_signal', data=dict(bogus='data'), source_id='bogus.sender.id')
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)

    def test_send_multiple(self):
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        for idx in range(3):
            AddonSignals.sendSignal('test_signal', data=dict(test='send_multiple', idx=idx))
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(dict(test='send_multiple', idx=2), callback.data)

    @staticmethod
    def test_register_multiple():
        data = dict(test='register_multiple')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=print)
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=xbmc.log)  # Debug
        AddonSignals.sendSignal('test_signal', data=data, source_id='plugin.sender.id')
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')

    def test_warning(self):
        data = dict(test='warning')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)  # Debug
        AddonSignals.sendSignal('test_signal', data=data, sourceID='plugin.sender.id')
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)

    @staticmethod
    def test_unregister_nonexisting():
        AddonSignals.unRegisterSlot('bogus.sender.id', signal='test_foo')
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_foo')
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_bar')

    def test_send_unregistered(self):
        data = dict(test='send_unregistered')
        AddonSignals.sendSignal('test_signal', data=data)
        self.assertNotEqual(data, callback.data)

    def test_send_nonsignal(self):
        data = dict(test='send_nonsignal')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        AddonSignals.sendSignal('test_signal', data=data)
        AddonSignals._jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id',
            message='test_nonsignal',
            data=dict(bogus='data'),
        ))
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)

    def test_send_none(self):
        data = dict(test='send_none')
        AddonSignals.registerSlot('plugin.sender.id', signal='test_signal', callback=callback)
        AddonSignals.sendSignal('test_signal', data=data)
        AddonSignals._jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
            sender='plugin.sender.id',
            message='test_nonsignal',
            data=None,
        ))
        AddonSignals.unRegisterSlot('plugin.sender.id', signal='test_signal')
        self.assertEqual(data, callback.data)
