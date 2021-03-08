# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring

# import unittest
# import lib.addonconnector

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.sender.id'


# def callback(data):
#     # xbmc.log('Received signal: %s' % data, 3)  # Warning
#     callback.data = data
#
#
# class TestSignals(unittest.TestCase):
#
#     def test_signals(self):
#         data = dict(test='signals')
#         register_callback('plugin.sender.id',  signal_name='test_signals', callback=callback)
#         make_signal_call('test_signals', data=data)
#         unregister_callback('plugin.sender.id', signal_name='test_signals')
#         self.assertEqual(data, callback.data)
#
#     def test_unicode(self):
#         data = dict(test='unicode', string='Föóbàr')
#         register_callback('plugin.sender.id',  signal_name='test_unicode', callback=callback)
#         make_signal_call('test_unicode', data=data)
#         unregister_callback('plugin.sender.id', signal_name='test_unicode')
#         self.assertEqual(data, callback.data)
#
#     def test_bogus_sender(self):
#         data = dict(test='bogus_sender')
#         register_callback('plugin.sender.id',  signal_name='test_bogus_sender', callback=callback)
#         make_signal_call('test_bogus_sender', data=data)
#         make_signal_call('test_bogus_sender', data=dict(bogus='data'), source_id='bogus.sender.id')
#         unregister_callback('plugin.sender.id', signal_name='test_bogus_sender')
#         self.assertEqual(data, callback.data)
#
#     def test_send_multiple(self):
#         register_callback('plugin.sender.id',  signal_name='test_multiple', callback=callback)
#         for idx in range(3):
#             make_signal_call('test_multiple', data=dict(test='send_multiple', idx=idx))
#         unregister_callback('plugin.sender.id', signal_name='test_multiple')
#         self.assertEqual(dict(test='send_multiple', idx=2), callback.data)
#
#     @staticmethod
#     def test_register_multiple():
#         data = dict(test='register_multiple')
#         register_callback('plugin.sender.id',  signal_name='test_register_multiple', callback=print)
#         register_callback('plugin.sender.id',  signal_name='test_register_multiple', callback=xbmc.log)  # Debug
#         make_signal_call('test_register_multiple', data=data, source_id='plugin.sender.id')
#         unregister_callback('plugin.sender.id', signal_name='test_register_multiple')
#
#     def test_warning(self):
#         data = dict(test='warning')
#         register_callback('plugin.sender.id',  signal_name='test_warning', callback=callback)  # Debug
#         make_signal_call('test_warning', data=data, sourceID='plugin.sender.id')
#         unregister_callback('plugin.sender.id', signal_name='test_warning')
#         self.assertEqual(data, callback.data)
#
#     @staticmethod
#     def test_unregister_nonexisting():
#         unregister_callback('bogus.sender.id', signal_name='test_foo')
#         unregister_callback('plugin.sender.id', signal_name='test_foo')
#         unregister_callback('plugin.sender.id', signal_name='test_bar')
#
#     def test_send_unregistered(self):
#         data = dict(test='send_unregistered')
#         make_signal_call('test_send_unregistered', data=data)
#         self.assertNotEqual(data, callback.data)
#
#     def test_send_nonsignal(self):
#         data = dict(test='send_nonsignal')
#         register_callback('plugin.sender.id',  signal_name='test_nonsignal', callback=callback)
#         make_signal_call('test_nonsignal', data=data)
#         _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
#             sender='plugin.sender.id',
#             message='test_nonsignal',
#             data=dict(bogus='data'),
#         ))
#         unregister_callback('plugin.sender.id', signal_name='test_nonsignal')
#         self.assertEqual(data, callback.data)
#
#     def test_send_none(self):
#         data = dict(test='send_none')
#         register_callback('plugin.sender.id',  signal_name='test_send_none', callback=callback)
#         make_signal_call('test_send_none', data=data)
#         _jsonrpc(method='JSONRPC.NotifyAll', params=dict(  # pylint: disable=protected-access
#             sender='plugin.sender.id.SIGNAL',
#             message='test_send_none',
#             data=[],
#         ))
#         unregister_callback('plugin.sender.id', signal_name='test_send_none')
#         self.assertEqual(None, callback.data)
