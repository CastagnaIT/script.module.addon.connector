# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

# pylint: disable=missing-docstring,invalid-name,reimported

import sys
import unittest

import lib.addonconnector as ac_sender
# To make the callbacks works on test environment we need of two different instances of the addonconnector module,
# then is needed delete the previous loaded module
del sys.modules['lib.addonconnector']
import lib.addonconnector as ac_service

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcaddon.ADDON_ID = 'plugin.example.id'


class TestClass:
    """Class test"""
    def __init__(self, value):
        self.value = value


def callback_call_pickle(first_object, second_object):
    # xbmc.log('Received RPC callback: {}, {}'.format(type(first_object), type(second_object)), 3)  # Warning
    callback_call_pickle.data = first_object, second_object
    return first_object, second_object


def callback_call_json(data):
    # xbmc.log('Received RPC callback: {}'.format(data), 3)  # Warning
    callback_call_json.data = data
    return dict(value='return_call', data=data)


def callback_string(data):
    # xbmc.log('Received RPC callback: {}'.format(data), 3)  # Warning
    callback_string.data = data
    return 'Föóbàr ԜՕȐŁǷ'


def callback_bogus_sender(data):
    # xbmc.log('Received RPC callback: {}'.format(data), 3)  # Warning
    callback_bogus_sender.data = data
    return dict(value='return_bogus_sender', data=data)


def callback_args_kwargs(first, second, third, fourth):
    # xbmc.log('Received RPC callback: {}, {}, {}, {}'.format(first, second, third, fourth), 3)  # Warning
    callback_args_kwargs.data = (first, second), dict(third=third, fourth=fourth)
    return third + fourth


def callback_send_multiple(idx):
    # xbmc.log('Received RPC callback: {}'.format(data), 3)  # Warning
    callback_send_multiple.data = idx
    return dict(idx=idx)


class TestCalls(unittest.TestCase):
    """Unit test for RPC make_call cases and RPC return callback"""
    ac_service.register_callback(callback_call_pickle)
    ac_service.register_callback(callback_call_json)
    ac_service.register_callback(callback_string)
    ac_service.register_callback(callback_bogus_sender)
    ac_service.register_callback(callback_args_kwargs)
    ac_service.register_callback(callback_send_multiple)

    def test_call_pickle(self):
        """Test with pickle serialization (callback with two arguments)"""
        call_cfg = ac_sender.CallConfig('callback_call_pickle')
        data = TestClass('FirstObject'), TestClass('SecondObject')
        ret = ac_sender.make_call(call_cfg, data[0], second_object=data[1])
        self.assertTrue(isinstance(ret, tuple))
        self.assertTrue(isinstance(ret[0], TestClass))
        self.assertTrue(isinstance(ret[1], TestClass))
        self.assertEqual(ret[0].value, data[0].value)
        self.assertEqual(ret[1].value, data[1].value)

    def test_call_json(self):
        """Test with JSON serialization (callback with one argument)"""
        call_cfg = ac_sender.CallConfig('callback_call_json',
                                       ser_type=ac_sender.SER_TYPE_JSON, ser_type_return=ac_sender.SER_TYPE_JSON)
        data = {'test': 1, 'name': 'Test with JSON serialization'}
        ret = ac_sender.make_call(call_cfg, data)
        self.assertEqual(data, callback_call_json.data)
        self.assertEqual(ret, dict(value='return_call', data=data))

    def test_call_string(self):
        """Test with no serialization (string)"""
        call_cfg = ac_sender.CallConfig('callback_string',
                                       ser_type=ac_sender.SER_TYPE_STRING, ser_type_return=ac_sender.SER_TYPE_STRING)
        data = 'Föóbàr'
        ret = ac_sender.make_call(call_cfg, data)
        self.assertEqual(data, callback_string.data)
        self.assertEqual(ret, 'Föóbàr ԜՕȐŁǷ')

    def test_bogus_sender(self):
        """Test with a bogus add-on ID target"""
        call_cfg = ac_sender.CallConfig('callback_bogus_sender', addon_id='bogus.sender.id', timeout_secs=1)
        with self.assertRaises(ac_sender.WaitTimeoutError) as cm:
            ac_sender.make_call(call_cfg, dict(bogus='data'))
        self.assertTrue(isinstance(cm.exception, ac_sender.WaitTimeoutError))

    def test_call_pickle_args_kwargs(self):
        """Test with pickle and multiple args and kwargs"""
        call_cfg = ac_sender.CallConfig('callback_args_kwargs')
        args = ('one', 'two')
        kwargs = dict(third=1, fourth=2)
        ret = ac_sender.make_call(call_cfg, *args, **kwargs)
        _args, _kwargs = callback_args_kwargs.data
        self.assertEqual(args, _args)
        self.assertEqual(kwargs, _kwargs)
        self.assertEqual(ret, 3)

    def test_send_multiple(self):
        """Test with multiple calls"""
        call_cfg = ac_sender.CallConfig('callback_send_multiple')
        for idx in range(3):
            ret = ac_sender.make_call(call_cfg, idx=idx)
            self.assertEqual(idx, callback_send_multiple.data)
            self.assertEqual(ret, dict(idx=idx))
