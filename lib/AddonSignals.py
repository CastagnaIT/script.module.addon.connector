# -*- coding: utf-8 -*-
# GNU Lesser General Public License v2.1 (see COPYING or https://www.gnu.org/licenses/gpl-2.1.txt)
"""The AddonSignals module provides signal/slot mechanism for inter-addon communication in Kodi"""

from xbmc import executeJSONRPC, log, LOGNOTICE, Monitor, sleep


class WaitTimeoutError(Exception):
    pass


def _perf_clock():
    """Provides high resolution timing in seconds"""
    if hasattr(time, 'perf_counter'):
        return time.perf_counter()  # pylint: disable=no-member
    if hasattr(time, 'clock'):
        # time.clock() was deprecated in Python 3.3 and removed in Python 3.8
        return time.clock()  # pylint: disable=no-member
    return time.time()  # Fallback


def _addon_id():
    """Return the Kodi add-on id and cache it as a static variable"""
    if not hasattr(_addon_id, 'cached'):
        from xbmcaddon import Addon
        _addon_id.cached = Addon().getAddonInfo('id')
    return getattr(_addon_id, 'cached')


def _decode_data(data):
    """Decode base64-encoded JSON data and return Python data structure"""
    import json
    encoded_data = json.loads(data)
    if not encoded_data:
        return None
    from base64 import b64decode
    json_data = b64decode(encoded_data[0])
    # NOTE: With Python 3.5 and older json.loads() does not support bytes or bytearray
    return json.loads(_to_unicode(json_data))


def _encode_data(data):
    """Encode Python data structure into base64-encoded JSON data"""
    from base64 import b64encode
    import json
    json_data = json.dumps(data)
    if not isinstance(json_data, bytes):
        json_data = json_data.encode('utf-8')
    encoded_data = b64encode(json_data)
    return encoded_data.decode('ascii')


def _receiver():
    """Return a SignalReceiver instance and cache it as a static variable"""
    if not hasattr(_receiver, 'cached'):
        _receiver.cached = SignalReceiver()
    return getattr(_receiver, 'cached')


def _jsonrpc(**kwargs):
    """Perform JSONRPC calls"""
    import json
    if 'id' not in kwargs:
        kwargs.update(id=0)
    if 'jsonrpc' not in kwargs:
        kwargs.update(jsonrpc='2.0')
    return json.loads(executeJSONRPC(json.dumps(kwargs)))


def _to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text


class SignalReceiver(Monitor, object):
    """The AddonSignals receiver class"""

    def __init__(self):  # pylint: disable=super-init-not-called
        """The SignalReceiver constructor"""
        self._slots = {}
        super(SignalReceiver, self).__init__()

    def registerSlot(self, signaler_id, signal, callback):
        """Register a slot in the AddonSignals receiver"""
        if signaler_id not in self._slots:
            self._slots[signaler_id] = {}
        self._slots[signaler_id][signal] = callback

    def unRegisterSlot(self, signaler_id, signal):
        """Unregister a slot in the AddonSignals receiver"""
        if signaler_id not in self._slots:
            return
        if signal not in self._slots[signaler_id]:
            return
        del self._slots[signaler_id][signal]

    def onNotification(self, sender, method, data):
        """The Kodi Monitor event handler for notifications"""
        if not sender.endswith('.SIGNAL'):
            return
        sender = sender[:-7]
        if sender not in self._slots:
            return
        signal = method.split('.', 1)[-1]
        if signal not in self._slots[sender]:
            return
        self._slots[sender][signal](_decode_data(data))


class CallHandler(object):
    """The AddonSignals event handler class"""

    def __init__(self, signal, data, source_id, timeout=1000, use_timeout_exception=False):
        ''' The CallHandler constructor '''
        self.signal = signal
        self.timeout = timeout
        self.source_id = source_id
        self._return = None
        self.is_callback_received = False
        self.use_timeout_exception = use_timeout_exception
        registerSlot(self.source_id, '_return.{0}'.format(self.signal), self.callback)
        sendSignal(signal, data, self.source_id)

    def callback(self, data):
        """Method to register function as callback"""
        self._return = data
        self.is_callback_received = True

    def waitForReturn(self):
        """Wait for callback to trigger"""
        monitor = xbmc.Monitor()
        end_time = _perf_clock() + (self.timeout / 1000)
        while not self.is_callback_received:
            if _perf_clock() > end_time:
                if self.use_timeout_exception:
                    unRegisterSlot(self.source_id, self.signal)
                    raise WaitTimeoutError
                break
            elif monitor.abortRequested():
                raise OSError
            xbmc.sleep(10)
        unRegisterSlot(self.source_id, self.signal)

        return self._return


def registerSlot(signaler_id, signal, callback):
    """
    Register a slot for a function callback
    :param signaler_id: the name used for call/answer (e.g. add-on id)
    :param signal: name of the function to call (can be the same used in returnCall/makeCall/...)
    :param callback: the function to call
    """
    _receiver().registerSlot(signaler_id, signal, callback)


def unRegisterSlot(signaler_id, signal):
    """API method to unregister a slot"""
    _receiver().unRegisterSlot(signaler_id, signal)


def sendSignal(signal, data=None, source_id=None, sourceID=None):
    """API method to send a signal"""
    if sourceID:
        log('++++==== script.module.addon.signals: sourceID keyword is DEPRECATED - use source_id ====++++', LOGNOTICE)
    _jsonrpc(method='JSONRPC.NotifyAll', params=dict(
        sender='%s.SIGNAL' % (source_id or sourceID or _addon_id()),
        message=signal,
        data=[_encode_data(data)],
    ))


def registerCall(signaler_id, signal, callback):
    """API method to register a callback slot"""
    registerSlot(signaler_id, signal, callback)


def returnCall(signal, data=None, source_id=None):
    """
    Make a return call to the target add-on
    :param signal: name of the function to call (can be the same used in registerSlot/makeCall/...)
    :param data: data to send
    :param source_id: the name used for call/answer (e.g. add-on id)
    """
    sendSignal('_return.{0}'.format(signal), data, source_id)


def makeCall(signal, data=None, source_id=None, timeout_ms=1000, use_timeout_exception=False):
    """
    Make a call to the source add-on
    :param signal: name of the function to call (can be the same used in registerSlot/returnCall/...)
    :param data: data to send
    :param source_id: the name used for call/answer (e.g. add-on id)
    :param timeout_ms: maximum waiting time before the timeout
    :param use_timeout_exception: if True when the timeout occurs will raise the exception 'TimeoutError'
             (allow to return 'None' value from the callback data)
    """
    return CallHandler(signal, data, source_id, timeout_ms, use_timeout_exception).waitForReturn()
