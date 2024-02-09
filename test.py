import torchaudio
import matplotlib
import matplotlib.pyplot as plt
import os
import torch

path = os.path.abspath('./music/elaina/audio.mp3')

waveform, sample_rate = torchaudio.load(path, format="mp3")

mfcc_transform = torchaudio.transforms.MFCC(sample_rate=sample_rate, n_mfcc=13)
mfcc = mfcc_transform(waveform)

# plot

time_axis = torch.linspace(0, waveform.shape[1] / sample_rate, waveform.shape[1])

plt.figure(figsize=(10, 5))
plt.figure()
plt.imshow(mfcc.log2()[0,:,:].numpy(), cmap='gray')
plt.show()

print("hello world")