from matplotlib import pyplot as plt
from torch import nn
import torch
import torchaudio


class AudioTransformPipeline(nn.Module):
        
    def __init__(self, orig_sr, ideal_sr, duration, hop_length=200):
        super().__init__()
        self.sample_rate = orig_sr
        self.ideal_sr = ideal_sr
        self.duration = duration
        self.hop_length = hop_length

        self.resample = torchaudio.transforms.Resample(
            orig_freq=self.sample_rate, new_freq=self.ideal_sr
        )
        self.spec = torchaudio.transforms.Spectrogram(hop_length=hop_length)
        self.stretch = torchaudio.transforms.TimeStretch()
        self.mel = torchaudio.transforms.MelScale()

    def forward(self, waveform):
        resampled = self.resample(waveform)
        # print(resampled.shape)
        
        spec_resampled = self.spec(resampled)
        # print(spec_resampled.shape)
        
        ideal_size2 = self.ideal_sr//self.hop_length*self.duration
        factor = spec_resampled.shape[2] / ideal_size2
        # print(factor)
        stretched = self.stretch(spec_resampled, factor).real
        
        # if (stretched)
        
        # print(stretched.shape)
        mel = torch.log1p(self.mel(stretched))

        return mel


def plot_mel(mel):
    plt.figure(figsize=(12, 4))
    plt.imshow(mel[0].detach().numpy(), cmap="viridis")
    plt.title("Mel Spectrogram")
    plt.xlabel("Time")
    plt.ylabel("Frequency")
    plt.show()


def load_audio(path):
    waveform, sample_rate = torchaudio.load(path)
    return waveform, sample_rate


if __name__ == "__main__":
    waveform, sample_rate = load_audio("../music/elaina/audio.mp3")
    pipeline = AudioTransformPipeline(sample_rate, 16000, 3)
    mel = pipeline(waveform)
    print(waveform.shape)
    plot_mel(mel)
