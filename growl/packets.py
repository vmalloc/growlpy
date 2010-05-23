## See LICENSE for license info
import struct
from cStringIO import StringIO
from hashlib import md5

_GROWL_VERSION = 1
_PACKET_TYPE_REGISTRATION = 0
_PACKET_TYPE_NOTIFICATION = 1
_GROWL_PRIORITIES = {0:0, 1:1, 2:2, -2:3, -1:4}

class SignedStructStream(object):
    def __init__(self):
        super(SignedStructStream, self).__init__()
        self._stream = StringIO()
        self._hash = md5()
    def writeBuffer(self, buff, sign=True):
        if sign:
            self._hash.update(buff)
        self._stream.write(buff)
    def sign(self):
        self.writeBuffer(self._hash.digest(), sign=False)
    def write(self, format, *data):
        packed = struct.pack(format, *data)
        self.writeBuffer(packed)
    def getvalue(self):
        return self._stream.getvalue()
    def gethash(self):
        return self._hash.digest()

def build_registration_packet(application_name, notifications):
    returned = SignedStructStream()
    returned.write("b", _GROWL_VERSION)
    returned.write("b", _PACKET_TYPE_REGISTRATION)
    returned.write("!H", len(application_name))
    returned.write("bb", len(notifications), len(notifications))
    returned.writeBuffer(application_name.encode('utf-8'))
    for notification in notifications:
        returned.write("!H", len(notification))
        returned.writeBuffer(notification.encode('utf-8'))
    for i in xrange(len(notifications)):
        returned.write("b", i)
    returned.sign()
    return returned.getvalue()


def build_notification_packet(application_name, notification_name, title, message, priority, sticky):
    flags = ((_GROWL_PRIORITIES.get(priority, 0) & 007) * 2)
    if sticky:
        flags |= 1
    returned = SignedStructStream()
    returned.write("!BBHHHHH",
                   _GROWL_VERSION,
                   _PACKET_TYPE_NOTIFICATION,
                   flags,
                   len(notification_name),           len(title),
                   len(message),
                   len(application_name),
                   )
    for x in (notification_name, title, message, application_name):
        returned.writeBuffer(x.encode('utf-8'))
    returned.sign()
    return returned.getvalue()
