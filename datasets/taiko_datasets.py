import os
import torch
import torch.utils.data
from utils.osu_reader import OsuTaikoReader
from preprocessing.audio import AudioTransformPipeline


class TaikoDataset(torch.utils.data.Dataset):
    bars_data: list[(int, int, list[int])]  # (reader_i, bar, array)

    def __init__(self, song_id, sample_rate=25600, hop_length=200, n_mels=128):
        self.song_id = song_id
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_mels = n_mels
        
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
                
        if len(self.readers) == 0:
            return None
        
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
        transformer = AudioTransformPipeline(self.audio.sample_rate, self.sample_rate, 1, n_mels=self.n_mels,hop_length=self.hop_length)
        processed_audio = transformer(audio)

        # Return the processed audio and the array
        # return (self.readers[reader_i].difficulty, processed_audio), torch.tensor(array)
        # Returns only audio for now
        return (self.readers[reader_i].difficulty/10,torch.tensor(processed_audio)), torch.tensor(array)

class TaikoDatasetDataset(torch.utils.data.Dataset):
    def __init__(self, folder, sample_rate=25600, hop_length=200, n_mels=128, train_test_split=0.8, train=True):
        self.folder = folder
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.is_train = train
        self.data = []

        # Add all ids to the data
        for song_id in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, song_id)):
                self.data.append(song_id)
                
        # Split data for testing and training
        self.data_train, self.data_test = torch.utils.data.random_split(self.data, [int(train_test_split * len(self.data)), len(self.data) - int(train_test_split * len(self.data))])
                                                                        
    def __len__(self):
        # return len(self.data)
        return len(self.data_train) if self.is_train else len(self.data_test)
    
    def __getitem__(self, idx):
        item = self.data_train[idx] if self.is_train else self.data_test[idx]
        return TaikoDataset(item, self.sample_rate, self.hop_length, self.n_mels)