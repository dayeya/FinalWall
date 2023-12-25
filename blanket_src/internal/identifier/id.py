import uuid
from dataclasses import dataclass

@dataclass
class RuleId:
    _id: str=""
    
    def init_id(self) -> None:
        self._id = uuid.uuid4().hex