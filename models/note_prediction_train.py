import os
import torch
import torch.optim as optim
import torch.nn as nn
import torch.utils.data as torchdata

from datasets.taiko_datasets import TaikoDataset
from models.note_prediction import NotePredictionModel

def train_note_prediction(epochs=1):
    model = NotePredictionModel(128, 64, 17)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Loss function
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # data loader
    music_folder = "./music"
    folder_ids = [int(f) for f in os.listdir(music_folder) if f.isnumeric()]

    for epoch in range(epochs):
        number_of_runs = 0
        
        running_loss = 0.0
        for id in folder_ids:
            dataloader = torchdata.DataLoader(TaikoDataset(id), batch_size=4, shuffle=True)
            
            try:
                for i, data in enumerate(dataloader):
                    inputs, labels = data
                    inputs, labels = inputs.to(device), labels.to(device, dtype=torch.float)
                    
                    # Zero the parameter gradients
                    optimizer.zero_grad()
                    
                    # Forward + backward + optimize
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    
                    number_of_runs += 1
                    
                    # Print statistics
                    running_loss += loss.item()
                    if number_of_runs % 2000 == 1999:
                        print(f"[{epoch + 1}, {number_of_runs + 1}] loss: {running_loss / 2000}")
                        running_loss = 0.0
            except Exception as e:
                print("Of courses it cannot be pastelite's code without some bugs")
                print(f"Error in {id}: {e}")
                continue
                
