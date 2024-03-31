
from web.db_utils import (
    get_availability,
    get_availabilities
)
class DBRow:
    def __init__(self, name):
        self.name=name
    
    def __eq__(self, other):
        self_vars = vars(self).items()
        other_vars = vars(self).items()
        if len(self_vars) != len(other_vars):
            return False
        for attribute in self_vars:
            if attribute[1] != getattr(other, attribute[0]):
                return False
        return True

r1 = DBRow("one")
r2 = DBRow("two")

if r1 == r2:
    print("equal")
else:
    print("not equal")

print(get_availabilities())