import uuid
from dataclasses import dataclass

@dataclass
class Id:
    _id: str=""
    
    def assign_id(self) -> None:
        self._id = uuid.uuid4().hex