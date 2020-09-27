# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""This file implements the Kodi xbmc module, either using stubs or alternative functionality"""

# pylint: disable=bad-option-value,too-few-public-methods,useless-object-inheritance
from __future__ import absolute_import, division, print_function, unicode_literals
import json
import time
import weakref

LOGLEVELS = ['Debug', 'Info', 'Notice', 'Warning', 'Error', 'Severe', 'Fatal', 'None']
LOGDEBUG = 0
LOGINFO = 1
LOGNOTICE = 2
LOGWARNING = 3
LOGERROR = 4
LOGSEVERE = 5
LOGFATAL = 6
LOGNONE = 7


class Monitor(object):
    """A stub implementation of the xbmc Monitor class"""
    _instances = set()

    def __init__(self, line='', heading=''):  # pylint: disable=unused-argument
        """A stub constructor for the xbmc Monitor class"""
        self.iteration = 0
        self._instances.add(weakref.ref(self))

    def abortRequested(self):
        """A stub implementation for the xbmc Keyboard class abortRequested() method"""
        self.iteration += 1
        print('Iteration: %s' % self.iteration)
        return self.iteration % 5 == 0

    def waitForAbort(self, timeout=None):  # pylint: disable=no-self-use
        """A stub implementation for the xbmc Monitor class waitForAbort() method"""
        try:
            time.sleep(timeout)
        except KeyboardInterrupt:
            return True
        except Exception:  # pylint: disable=broad-except
            return True
        return False

    @classmethod
    def getinstances(cls):
        """Return the instances for this class"""
        dead = set()
        for ref in cls._instances.copy():
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead


def executeJSONRPC(jsonrpccommand):
    """A reimplementation of the xbmc executeJSONRPC() function"""
    command = json.loads(jsonrpccommand)

    ret = dict(id=command.get('id'), jsonrpc='2.0', result='OK')
    if command.get('method') == 'JSONRPC.NotifyAll':
        # Send a notification to all instances of subclasses
        for sub in Monitor.__subclasses__():
            for obj in sub.getinstances():
                obj.onNotification(
                    sender=command.get('params').get('sender'),
                    method=command.get('params').get('message'),
                    data=json.dumps(command.get('params').get('data')),
                )
    else:
        log("executeJSONRPC does not implement method '{method}'".format(**command), LOGERROR)
        return json.dumps(dict(error=dict(code=-1, message='Not implemented'), id=command.get('id'), jsonrpc='2.0'))
    return json.dumps(ret)


def log(msg, level=0):
    """A reimplementation of the xbmc log() function"""
    color1 = '\033[32;1m'
    color2 = '\033[32;0m'
    name = LOGLEVELS[level]
    if level in (4, 5, 6, 7):
        color1 = '\033[31;1m'
        if level in (6, 7):
            raise Exception(msg)
    elif level in (2, 3):
        color1 = '\033[33;1m'
    elif level == 0:
        color2 = '\033[30;1m'
    print('{color1}{name}: {color2}{msg}\033[39;0m'.format(name=name, color1=color1, color2=color2, msg=msg))


def sleep(timemillis):
    """A reimplementation of the xbmc sleep() function"""
    time.sleep(timemillis / 1000)
