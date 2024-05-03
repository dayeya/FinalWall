from dataclasses import dataclass
from src.internal.system.transaction import Transaction
from src.internal.system.logging import LogObject

CONNECTION = "Connection"
DISCONNECTION = "Disconnection"
AUTHORIZED_REQUEST = "Authorized Request"
UNAUTHORIZED_REQUEST = "Unauthorized Request"


@dataclass(slots=True)
class Event:
    """
    A class representing an event made by the user.

    Attributes
    ----------
    kind: str - The kind of the event.
        disconnection - client ended a connection stream.
        connection: client just connected, seldom by sending a request.
                    For bots that just connect without sending a request this event is useful.
        authorized_request: client sent an authorized request without any malicious data.
        unauthorized_request: client sent an unauthorized request. In cases where the engine blocks clients
                            even before receiving requests from them, the Event.tx field will be None.
                            Happens when client is dirty - Geolocation or banned software.
    id: str - unique id.
        In cases where Event.tx is None the id will be tokenized.
        Otherwise, it's the tx.id.
    log: LogObject - log of the event.
         Either security log or access log or None.
    tx: Transaction - The transaction that triggered the event.
    """
    kind: str
    id: str
    log: LogObject | None
    tx: Transaction | None
