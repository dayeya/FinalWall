from dataclasses import dataclass

@dataclass(slots=True)
class Rule:
    _id: str
    _desc: str
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def desc(self) -> str:
        return self._desc