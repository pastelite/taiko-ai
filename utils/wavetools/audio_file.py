import librosa
import torchaudio
import torch
import warnings

class AudioFile:
    waveform: torch.Tensor
    sr: int
    
    def __init__(self, path):
        self.path = path
        self.waveform = None
        self.sr = None
        
    def __str__(self):
        return f"AudioFile({self.path})"
    
    def duration(self):
        return librosa.get_duration(path=self.path)*1000
    
    def sample_rate(self):
        if self.waveform is None:
            raise ValueError("Waveform not loaded")
        return self.sr
    
    def load_waveform(self):
        self.waveform, self.sr = torchaudio.load(self.path)
        return 
    
    def is_loaded(self):
        return self.waveform is not None
    
    def __getitem__(self,key):
        if self.waveform is None:
            raise ValueError("Waveform not loaded")
           
        if isinstance(key, slice):
            return self.waveform[:,int(key.start*self.sr/1000):int(key.stop*self.sr/1000)]
    
# class LoadedAudioFile(AudioFile):
#     waveform: torch.Tensor
#     sample_rate: int    
    
#     def __init__(self,path):
#         super().__init__(path)
#         self.waveform, self.sample_rate = torchaudio.load(path)
        
#     def __getitem__(self,key):
#         if isinstance(key, slice):
#             # return self.waveform[:,0:1]
#             return self.waveform[:,int(key.start*self.sample_rate/1000):int(key.stop*self.sample_rate/1000)]
        
    
        