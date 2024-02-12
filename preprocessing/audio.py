from matplotlib import pyplot as plt
from torch import nn
import torch
import torchaudio

class AudioTransformPipeline(nn.Module):
    def __init__(self, sample_rate, ideal_sr, duration):
        super().__init__()
        self.sample_rate = sample_rate
        self.ideal_sr = ideal_sr
        self.duration = duration
        
        self.resample = torchaudio.transforms.Resample(orig_freq=self.sample_rate, new_freq=self.ideal_sr)
        self.spec = torchaudio.transforms.Spectrogram()
        self.stretch = torchaudio.transforms.TimeStretch()
        self.mel = torchaudio.transforms.MelScale()

    def forward(self, waveform):
        factor = (self.sample_rate * self.duration)/waveform.shape[1]
        resampled = self.resample(waveform)
        spec_resampled = self.spec(resampled)
        stretched = self.stretch(spec_resampled,1/factor).real
        mel = torch.log1p(self.mel(stretched))
        
        return mel
    
def plot_mel(mel):
    plt.figure(figsize=(12, 4))
    plt.imshow(mel[0].detach().numpy(), cmap='viridis')
    plt.title('Mel Spectrogram')
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.show()
    
def load_audio(path):
    waveform, sample_rate = torchaudio.load(path)
    return waveform, sample_rate

if __name__ == "__main__":
    waveform, sample_rate = load_audio("../music/elaina/audio.mp3")
    pipeline = AudioTransformPipeline(sample_rate, 16000, 3)
    mel = pipeline(waveform)
    plot_mel(mel)