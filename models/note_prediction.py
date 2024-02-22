import torch
from torch import nn
from torchsummary import summary

class NotePredictionModel(torch.nn.Module):
    def __init__(self, input_size=128, hidden_size=64, output_size=17):
        super(NotePredictionModel,self).__init__()
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
        
        # attention layer
        self.attn_fc = nn.Linear(hidden_size+1, hidden_size)
        self.attn = nn.Linear(hidden_size, 1)
        
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x, diff):
        # diff = torch.tensor(diff, dtype=torch.float32).unsqueeze(0)
        
        x = self.conv1(x)
        # print(x.shape)
        x = self.conv2(x)
        # print(x.shape)
        x = self.flatten(x)
        # print(x.shape)
        x = self.fc1(x)
        # print(x.shape)
        
        # print(diff.shape, x.shape)
        combined = torch.cat((diff, x),-1)
        combined = self.attn_fc(combined)
        attn = self.attn(combined)
        # print(attn.shape)
        x = x*attn
        
        # print(x.shape)
        x = self.fc2(x)
        return x
    
    ## Note: diff have to be unsqueezed to be concatenated with x
    def predict(self, x, diff):
        return self.forward(x, diff)

def note_prediction_model_summary():
    summary(NotePredictionModel(128, 64, 17), [(1, 128, 128),[1]])
        
                        