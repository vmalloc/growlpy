import socket
from packets import build_registration_packet
from packets import build_notification_packet

_GROWL_UDP_PORT = 9887

_HOST_NAME = socket.gethostname()
_DEFAULT_TITLE = "From %s" % _HOST_NAME

APPLICATION_NAME = "growlpy"
NOTIFICATION_NAME = 'Notification'

def send_growl(host, message,
          title=_DEFAULT_TITLE,
          port=_GROWL_UDP_PORT,
          sticky=False,
          priority=0,
          notification = NOTIFICATION_NAME,
          application = APPLICATION_NAME,
          _socket=socket.socket,
          _build_notification_packet=build_notification_packet,
          _build_registration_packet=build_registration_packet,
          ):
    s = _socket(socket.AF_INET, socket.SOCK_DGRAM)
    reg_packet = _build_registration_packet(application_name=application, notifications=[notification])

    s.sendto(reg_packet, (host, port))

    notification = _build_notification_packet(
        priority=priority,
        message=message,
        title=title,
        notification_name=notification,
        application_name=application,
        sticky=sticky)

    s.sendto(notification, (host, port))
    s.close()
