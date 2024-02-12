import librosa
import torchaudio
import torch

class AudioFile:
    def __init__(self, path):
        self.path = path
        
    def __str__(self):
        return f"AudioFile({self.path})"
    
    def duration(self):
        return librosa.get_duration(path=self.path)*1000
    
    def load_waveform(self):
        return LoadedAudioFile(self.path)
    
class LoadedAudioFile(AudioFile):
    waveform: torch.Tensor
    sample_rate: int    
    
    def __init__(self,path):
        super().__init__(path)
        self.waveform, self.sample_rate = torchaudio.load(path)
        
    def __getitem__(self,key):
        if isinstance(key, slice):
            # return self.waveform[:,0:1]
            return self.waveform[:,int(key.start*self.sample_rate/1000):int(key.stop*self.sample_rate/1000)]
        
    
        