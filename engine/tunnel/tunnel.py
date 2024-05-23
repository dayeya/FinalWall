from enum import StrEnum
from flask_socketio import SocketIO


class TunnelEvent(StrEnum):
    AccessLogUpdate = 'access_log_update'
    SecurityLogUpdate = 'security_log_update'


class Tunnel(SocketIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def register_event(self, event: TunnelEvent, data):
        self.emit(event.name, data)
