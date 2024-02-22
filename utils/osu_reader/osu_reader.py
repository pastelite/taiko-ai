import os
import pprint
import re
from enum import Enum, IntEnum
from typing import Generator, Iterator, Optional
import librosa
import torchaudio

import utils.osu_reader.timing_points as tp
import utils.osu_reader.hit_objects as ho

from utils.wavetools.audio_file import AudioFile


# class Audio:
#     def __init__(self, path):
#         self.path = path

#     def __str__(self):
#         return f"Path: {self.path}"

#     def duration(self):
#         return librosa.get_duration(path=self.path)

#     def load_waveform(self):
#         self.waveform, self.sr = torchaudio.load(self.path)
#         return self.waveform, self.sr
    
#     def is_loaded(self):
#         return hasattr(self, 'waveform')

#     def __getitem__(self, key):
#         if isinstance(key, slice):
#             return self.waveform[key[0] * self.sr / 1000, key[1] * self.sr / 1000]


class OsuTaikoReader:
    general: dict[str, str]
    editor: dict[str, str]
    metadata: dict[str, str]
    # difficulty: dict[str, str]
    timing_points: tp.TimingPoints
    hit_objects: ho.HitObjects
    difficulty: Optional[float]
    audio: AudioFile

    def __init__(self, path):
        self.path = path
        self.file = open(path, "r")

        data = self._parse_file()
        self._format_data(data)
        
        # check mode
        if int(self.general["Mode"]) != 1:
            raise ValueError("Invalid mode. Only taiko mode is supported.")
        
        self._parse_difficulty()
        self._parse_audio()
        
        

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
            if line.startswith("osu"): # osu file version
                continue
            
            if cur_header == "":
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
            time = round(float(splitted[2]))
            hit_sound = ho.HitType.from_osu(round(float(splitted[4])))
            parsed.append((time, hit_sound))
        return ho.HitObjects(parsed)

    def _parse_timing_points(self, timing_points: list[str]):
        return tp.TimingPoints(timing_points)

    def _parse_difficulty(self):
        try:
            with open(
                os.path.join(os.path.dirname(self.path), "difficulty.txt"), "r"
            ) as file:
                difficulty = eval(file.read())
                self.difficulty = difficulty[self.metadata["Version"]]
        except:
            self.difficulty = None

    def _parse_audio(self):
        audio_filename = self.general["AudioFilename"]
        audio_path = os.path.join(os.path.dirname(self.path), audio_filename)
        self.audio = AudioFile(audio_path)
        
    def load_audio(self):
        self.audio.load_waveform()

    def bars_and_arrays(self) -> Generator[tuple[tuple[int, int], list[int]], None, None]:
        duration = self.audio.duration()
        beats = self.timing_points.beats_point(duration)
        # meter = self.timing_points.data[0].meter
        meter = 4 #only support 4/4 time signature, for now
        
        # print(f"{duration=} {beats=} {meter=}")

        bars: list[tuple[int,int]] = []

        for i in range(0, int(len(beats) / meter)):
            beats_in_bar = beats[i * meter : ((i + 1) * meter + 1)]
            bars.append((beats_in_bar[0], beats_in_bar[-1] - 1))

        # print("barsss",bars)

        for bar in bars:
            if bar[0] >= bar[1]:
                continue
            if bar[0] < 0 or bar[1] > duration:
                continue
            
            progress = lambda x: (x - bar[0]) / (bar[1] - bar[0])
            noteobjects = self.hit_objects[bar[0] : bar[1]]
            objects = [(progress(note[0]) * 16, note[1]) for note in noteobjects]

            arr = [0] * 17
            for note in objects:
                arr[round(note[0])] = 1

            yield (bar, arr)


if __name__ == "__main__":
    reader = OsuTaikoReader(
        "../music/1342378/Ueda Reina - Literature (TV Size) (-Aqua) [Ashen].osu"
    )
    print(reader)
    print(reader.audio.path)
    print(reader.audio.duration())
    print(list(reader.bars_and_arrays()))
