#
# FinalWall - An Event representation.
# Author: Dayeya
#

import json
import pickle
from dataclasses import dataclass

from .logs import LogObject
from ..core.transaction import Transaction

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
    request: Transaction - The transaction that triggered the event.
    response: Transaction - The transaction that triggered the event.
    """
    kind: str
    id: str
    log: LogObject | None
    request: Transaction | None
    response: Transaction | None

    @classmethod
    def serialize(cls, event) -> bytes:
        """Serializes `Self` using Pickle protocol."""
        return pickle.dumps(event)

    @classmethod
    def deserialize(cls, pickled_event: bytes):
        return pickle.loads(pickled_event)

    @classmethod
    def json_deserialize(cls, event):
        return json.loads(event)
