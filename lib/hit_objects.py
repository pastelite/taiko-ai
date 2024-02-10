from enum import IntEnum


class HitType(IntEnum):
    INVALID = 0
    DON = 1
    KAT = 2
    BIG_DON = 3
    BIG_KAT = 4

    def from_osu(input: int):
        switcher = {
            0: HitType.DON,
            8: HitType.KAT,
            4: HitType.BIG_DON,
            12: HitType.BIG_KAT,
        }
        return switcher.get(input, HitType.INVALID)

    def to_int(self):
        return int(self)


class HitObjects:
    data: list[(int, HitType)]

    def __init__(self, data: list[(int, HitType)]):
        self.data = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [
                object
                for object in self.data
                if object[0] >= key.start and object[0] <= key.stop
            ]
        if isinstance(key, int):
            for object in self.data:
                if object[0] > key:
                    return None
                if object[0] == key:
                    return object

    def __str__(self):
        return str(self.data)
