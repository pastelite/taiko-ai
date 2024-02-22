from collections import namedtuple
import os
from typing import cast
import torch
import torch.optim as optim
import torch.nn as nn
import torch.utils.data as torchdata

from dataloader.taiko_datasets import TaikoDataset
from models.note_prediction import NotePredictionModel
from utils.type import NotePredictionCheckpoint


def train_note_prediction(
    model: NotePredictionModel,
    music_folder="./data/music",
    ideal_size: tuple[int, int] = (128, 128),
    epochs=1,
    continue_checkpoint: str = None,
    save_checkpoint_dir: str = "./models/note_prediction_checkpoints/",
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Loss function
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # data loader
    dirs_in_folder = []
    for root, dirs, files in os.walk(music_folder):
        for d in dirs:
            dirs_in_folder.append(os.path.join(root, d))
            
    start_epoch = 0
    if continue_checkpoint is not None:
        state = torch.load(continue_checkpoint)
        state = cast(NotePredictionCheckpoint, state)
        model.load_state_dict(state.modeldict)
        optimizer.load_state_dict(state.optimizerdict)
        start_epoch = state.epoch + 1
        print("checkpoint loaded")

    print("data loaded, proceed to training")

    for epoch in range(start_epoch,epochs+start_epoch):
        print("Starting Training for epoch", epoch)
        number_of_runs = 0

        running_loss = 0.0
        combined_loss = 0.0
        for id in dirs_in_folder:
            dataloader = torchdata.DataLoader(
                TaikoDataset(id,ideal_size), batch_size=4, shuffle=True
            )

            try:
                for i, data in enumerate(dataloader):
                    # data = cast(tuple[torch.Tensor, torch.Tensor],data)
                    audio, diff, labels = data
                    # audio, diff = input
                    diff = diff.unsqueeze(1)

                    diff, audio, labels = (
                        diff.to(device, dtype=torch.float),
                        audio.to(device, dtype=torch.float),
                        labels.to(device, dtype=torch.float),
                    )

                    # Zero the parameter gradients
                    optimizer.zero_grad()
                    
                    print("audio",audio.shape)

                    # Forward + backward + optimize
                    outputs = model(audio, diff)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    number_of_runs += 1

                    # Print statistics
                    running_loss += loss.item()
                    combined_loss += loss.item()
                    if number_of_runs % 2000 == 1999:
                        print(
                            f"[{epoch + 1}, {number_of_runs + 1}] loss: {running_loss / 2000}"
                        )
                        running_loss = 0.0

            except Exception as e:
                print("Of courses it cannot be pastelite's code without some bugs")
                print(f"Error in {id}: {e}")
                continue

        # Save the model
        print("Finished Training for epoch", epoch)
        print(f"{epoch=} loss: {combined_loss / number_of_runs}")
        state = NotePredictionCheckpoint(epoch, model.state_dict(), optimizer.state_dict(), ideal_size)
        save_path = os.path.join(save_checkpoint_dir, f"note_prediction_model_{epoch}.pt")
        torch.save(state, save_path)
