#
# FinalWall - JsonSerializer will convert *Transactions* and *Events* to json format,
#             For correct data exchange between the API and the WAF.
# Author: Dayeya.
#

import json
from typing import Union
from dataclasses import asdict

from ..events import Event
from ..core.transaction import Transaction
from finalwall.http_process import decode_headers


class JsonSerializer:
    @classmethod
    def transaction(cls, tx: Transaction) -> Union[Transaction, None]:
        if tx is None:
            return None
        return Transaction(
            owner=tx.owner,
            real_host_address=tx.real_host_address,
            raw=tx.raw.decode("utf-8"),
            creation_date=tx.creation_date,
            method=tx.method.decode("utf-8"),
            url=tx.url,
            version=tx.version.decode("utf-8"),
            query_params=tx.query_params,
            headers=decode_headers(tx.headers),
            body=tx.body,
            size=tx.size
        )

    @classmethod
    def event(cls, event: Event):
        temp = Event(kind=event.kind, id=event.id, log=event.log,
                     request=cls.transaction(event.request),
                     response=cls.transaction(event.response))
        return json.dumps(asdict(temp))

    def __call__(self, jsonable: object):
        if isinstance(jsonable, Transaction):
            return self.transaction(jsonable)
        elif isinstance(jsonable, Event):
            return self.event(jsonable)
        else:
            raise Exception(f"{jsonable} of type {type(jsonable)} is not Jsonable for the Jsonizer.")
