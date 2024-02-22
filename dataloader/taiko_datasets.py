import os
import torch
import torch.utils.data
from utils.osu_reader import OsuTaikoReader
from utils.general import clamp, coalesce
from dataloader.audio_pipeline import AudioTransformPipeline

# def if_null_return(s,d):
#     if s is None:
#         return d
#     else:
#         return s


class TaikoDataset(torch.utils.data.Dataset):
    bars: list[tuple[OsuTaikoReader, int, list[int]]]  # (reader_i, bar, array)

    def __init__(self, song_folder, ideal_size: tuple[int,int], hop_length=200):
        self.song_id = song_folder
        self.ideal_size = ideal_size
        self.hop_length = hop_length
        
        self.bars = []
        
        osu_files = [f for f in os.listdir(song_folder) if f.endswith(".osu")]

        self.readers: list[OsuTaikoReader]  = []
        for f in osu_files:
            try:
                self.readers.append(OsuTaikoReader(os.path.join(song_folder, f)))
            except ValueError as e:
                print(f"Error reading {f}: {e}, skipping...")
                
        if len(self.readers) == 0:
            return None
        
        self.audio = self.readers[0].audio
        self.audio.load_waveform()

        # Load all bars
        for reader in self.readers:
            for bar, array in reader.bars_and_arrays():
                if torch.sum(torch.tensor(array)) > 0:
                    self.bars.append((reader, bar, array))

    def __len__(self):
        return len(self.bars)

    def __getitem__(self, idx: int):
        reader, bar, array = self.bars[idx]

        # Load the audio
        # if reader.audio.is_loaded() == False:
        #     reader.audio.load_waveform()
        
        audio = self.audio[bar[0]:bar[1]]
        transformer = AudioTransformPipeline(self.audio.sample_rate(),self.ideal_size[0],self.ideal_size[1],self.hop_length)
        processed_audio = transformer(audio)
        
        difficulty = clamp(coalesce(reader.difficulty, 0.0), 0, 10.0)

        return torch.tensor(processed_audio), difficulty, torch.tensor(array)

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