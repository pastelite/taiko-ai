import os
import torch
import torch.utils.data
from utils.osu_reader import OsuTaikoReader
from preprocessing.audio import AudioTransformPipeline


class TaikoDataset(torch.utils.data.Dataset):
    bars_data: list[(int, int, list[int])]  # (reader_i, bar, array)

    def __init__(self, song_id):
        self.song_id = song_id
        self.bars_data = []

        # Load the folder and music
        music_folder = os.path.normpath(
            os.path.join(os.path.dirname(__file__), f"../music/{song_id}")
        )
        osu_files = [f for f in os.listdir(music_folder) if f.endswith(".osu")]

        self.readers = []
        for f in osu_files:
            try:
                self.readers.append(OsuTaikoReader(os.path.join(music_folder, f)))
            except ValueError as e:
                print(f"Error reading {f}: {e}, skipping...")
        
        self.audio = self.readers[0].audio.load_waveform()

        # Load all bars
        for reader_i, reader in enumerate(self.readers):
            # print(self.readers[reader_i].audio.duration())
            # print(reader.bars_arrays())
            for bar, array in reader.bars_arrays():
                # print(bar, array)
                if torch.sum(torch.tensor(array)) > 0:
                    self.bars_data.append((reader_i, bar, array))

        # print(self.bars_data)

    def __len__(self):
        return len(self.bars_data)

    def __getitem__(self, idx):
        reader_i, bar, array = self.bars_data[idx]
        # print(reader_i, bar, array)

        # Load the audio
        audio = self.audio[bar[0] : bar[1]]
        transformer = AudioTransformPipeline(self.audio.sample_rate, 16000, 1)
        processed_audio = transformer(audio)

        # Return the processed audio and the array
        return (self.readers[reader_i].difficulty, processed_audio), torch.tensor(array)
