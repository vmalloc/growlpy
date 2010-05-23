import socket
from unittest2 import TestCase
from cStringIO import StringIO
from hashlib import md5
import struct
import mox

from growl.packets import build_registration_packet
from growl.packets import build_notification_packet
from growl.packets import _GROWL_PRIORITIES
from growl import send_growl

class PacketTest(TestCase):
    def setUp(self):
        super(PacketTest, self).setUp()
        self.mox = mox.Mox()
    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        super(PacketTest, self).tearDown()
    def _test__growl_sending(self, sticky):
        application = "some app"
        notification = "some notification"
        title = "my title"
        priority = 1337
        message = "blap"
        host = "192.168.1.120"
        port = 331337

        constructed_registration_packet = "constructed_reg"
        constructed_notification_packet = "constructed_notification"

        s = self.mox.CreateMockAnything()
        fake_socket = self.mox.CreateMockAnything()
        fake_socket(socket.AF_INET, socket.SOCK_DGRAM).AndReturn(s)

        registration_builder = self.mox.CreateMockAnything()
        notification_builder = self.mox.CreateMockAnything()

        registration_builder(
            application_name=application,
            notifications=[notification]).AndReturn(constructed_registration_packet)

        s.sendto(constructed_registration_packet,
                 (host, port))
        notification_builder(
            application_name=application,
            notification_name=notification,
            message=message,
            title=title,
            sticky=sticky,
            priority=priority,
            ).AndReturn(constructed_notification_packet)
        s.sendto(constructed_notification_packet,
                 (host, port))
        s.close()
        
        self.mox.ReplayAll()
        send_growl(
            host=host,
            title=title,
            sticky=sticky,
            priority=priority,
            notification=notification,
            message = message,
            application=application,
            port=port,
            _build_notification_packet = notification_builder,
            _build_registration_packet = registration_builder,
            _socket = fake_socket,
            )
    def test__growl_sending(self):
        for sticky in (True, False):
            self._test__growl_sending(sticky)
    
    def test__registration_packet(self):
        # reference: http://growl.info/documentation/developer/protocol.php
        appname = u"appname"
        notifications = ['hey']

        expected_data = StringIO()
        # version 1, type=registration
        expected_data.write("\x01\x00")
        # length of app name
        expected_data.write("\x00\x07")
        # number of notifications, num enabled
        expected_data.write("\x01\x01")
        expected_data.write(appname)
        # length of notification
        expected_data.write("\x00\x03")
        expected_data.write(notifications[0])
        # defaults
        expected_data.write("\x00")
        expected_data.write(md5(expected_data.getvalue()).digest())

        data = build_registration_packet(appname, notifications)
        self.assertEquals(expected_data.getvalue(), data)
    def _test__notification_packet(self, priority, sticky):
        appname = "appname"
        message = "some message"
        title = "some title"
        notification = "my notification"

        expected_data = StringIO()
        # version, type 'notification'
        expected_data.write("\x01\x01")
        expected_flags = ((_GROWL_PRIORITIES[priority] & 007) << 1)
        expected_flags |= 1 if sticky else 0
        expected_data.write("\x00")
        expected_data.write(chr(expected_flags))
        expected_data.write(struct.pack("!H", len(notification)))
        expected_data.write(struct.pack("!H", len(title)))
        expected_data.write(struct.pack("!H", len(message)))
        expected_data.write(struct.pack("!H", len(appname)))
        for x in (notification, title, message, appname):
            expected_data.write(x.encode('utf-8'))

        expected_data.write(md5(expected_data.getvalue()).digest())
            
        data = build_notification_packet(
            priority=priority,
            message=message,
            title=title,
            application_name=appname,
            notification_name=notification,
            sticky=sticky,
            )
        self.assertEquals(data, expected_data.getvalue())

    def test__notification_packet(self):
        for priority in xrange(-2, 3):
            for sticky in (True, False):
                self._test__notification_packet(priority=priority, sticky=sticky)

