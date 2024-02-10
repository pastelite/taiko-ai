import pprint
import re
from enum import Enum, IntEnum
import timing_points as tp
import hit_objects as ho

# from lib import TimingPoint


class OsuTaikoReader:
    general: dict[str, str]
    editor: dict[str, str]
    metadata: dict[str, str]
    difficulty: dict[str, str]
    timing_points: tp.TimingPoints
    hit_objects: ho.HitObjects

    def __init__(self, path):
        self.path = path
        self.file = open(path, "r")

        data = self._parse_file()
        self._format_data(data)

    def __str__(self):
        return f"General: {self.general}\nEditor: {self.editor}\nMetadata: {self.metadata}\nDifficulty: {self.difficulty}\nTiming Points: {self.timing_points}\nHit Objects: {self.hit_objects}"

    def _parse_file(self) -> dict[str, list[(str, str)]]:
        self.file.seek(0)
        data = {}
        cur_header = ""

        # parse all lines into a dictionary
        for line in self.file:
            line = line.strip()

            if line == "":  # empty line
                continue
            if line[0] == "/":  # comment
                continue
            if line.startswith("["):  # header
                cur_header = line[1:-1]
                data[cur_header] = []
                continue

            if line[0].isalpha():
                # key-value pair
                splitted = line.split(":", 1)
                if len(splitted) == 1:
                    continue
                key, value = map(lambda x: x.strip(), splitted)
                data[cur_header].append((key, value))
            else:
                # Object
                data[cur_header].append(("", line))

        return data

    def _format_data(self, data: dict[str, list[(str, str)]]):
        self.general = dict(data["General"])
        self.editor = dict(data["Editor"])
        self.metadata = dict(data["Metadata"])
        self.difficulty = dict(data["Difficulty"])
        self.timing_points = self._parse_timing_points(
            list(map(lambda x: x[1], data["TimingPoints"]))
        )
        self.hit_objects = self._parse_hit_objects(
            list(map(lambda x: x[1], data["HitObjects"]))
        )

    def _parse_hit_objects(self, hit_objects: list[str]):
        parsed = []
        for hit_object in hit_objects:
            splitted = hit_object.split(",")
            time = int(splitted[2])
            hit_sound = ho.HitType.from_osu(int(splitted[4]))
            parsed.append((time, hit_sound))
        return ho.HitObjects(parsed)

    def _parse_timing_points(self, timing_points: list[str]):
        return tp.TimingPoints(timing_points)


if __name__ == "__main__":
    reader = OsuTaikoReader(
        "../music/elaina/Ueda Reina - Literature (TV Size) (-Aqua) [Ashen].osu"
    )
    print(reader.hit_objects[5000:10000])
