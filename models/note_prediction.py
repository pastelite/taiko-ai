import torch
from torch import nn
from torchsummary import summary

class NotePredictionModel(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NotePredictionModel, self).__init__()
        # Simple one because this is my first time
        self.conv1 = nn.Sequential(
                        nn.Conv2d(1, 32, kernel_size=3, padding=1),
                        nn.ReLU(),
                        nn.MaxPool2d(2)
                    )
        self.conv2 = nn.Sequential(
                        nn.Conv2d(32, 64, kernel_size=3, padding=1),
                        nn.ReLU(),
                        nn.MaxPool2d(2)
                    )
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(64*input_size//4*input_size//4, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.fc2(x)
        return x
    
    def predict(self, x):
        return self.forward(x)

def note_prediction_model_summary():
    summary(NotePredictionModel(128, 64, 17), (1, 128, 128))
        
                        