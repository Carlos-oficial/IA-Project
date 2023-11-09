from typing import Dict


class Place:
    def __init__(self, name: str):
        self.name = name
        self.storage: Dict[str,int] = {}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
