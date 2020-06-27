# -*- coding: utf-8 -*-
import os
import sys
import time
import math
import random
import librosa
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from mutagen.mp3 import MP3


import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
from torchvision import transforms, utils
from torch.utils.data import Dataset, DataLoader


# Ignore warnings
import warnings
warnings.filterwarnings("ignore")



# seeding function for reproducibility
def seed_everything(seed):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True

'''
Preprocessing
'''

train = pd.read_csv('./FSong10.csv')
test = pd.read_csv('./test.csv', header = None)

train['path'] = './Records10/'+train['filename']

#submission = pd.read_csv('./sub.csv')


print(train.head())


SEED = 42
FRAC = 0.2     # Validation fraction
SR = 32000     # sampling rate
MAXLEN = 60    # seconds
N_MELS = 128
batch_size = 8

seed_everything(SEED)
device = torch.device('cuda')


#Random sample of 10 birds to test code.
classes = set(random.sample(train['specie'].unique().tolist(), 10)) 
print(classes)

class BirdSoundDataset(Dataset):

    def __init__(self, df):
        self.df = df

    def __len__(self):
        return len(self.df)
    
    
    def loadMP3(self, path, duration):
        try:
            audio, sample_rate = librosa.load(path, 
                                              sr=SR, 
                                              mono=True, 
                                              offset=0.0,
                                              duration=duration, 
                                              res_type='kaiser_fast')
            mels = librosa.feature.melspectrogram(y=audio, sr=SR,n_mels=N_MELS)
            return mels
            # mels will be of shape (N_MELS, ceil(duration*SR/512)) 
            # 512 here is default hop length

        except Exception as e:
            print("Error encountered while parsing file: ", path, e)
            mels = np.zeros((N_MELS, MAXLEN*SR//512), dtype=np.float32)
            return mels
            

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        path = self.df['path'].iloc[idx]
        duration = self.df['duration'].iloc[idx]
        if duration < MAXLEN:
            duration = None # read entire file
        else:
            duration = MAXLEN
        mfcc = self.loadMP3(path, duration)
        label  = self.df['label'].iloc[idx]
        sample = {'label':label, 'features': mfcc, 'duration': duration}
        return sample

# Train Val split
train = train.sample(frac=1).reset_index(drop=True)
train_len = int(len(train) * (1-FRAC))
train_df = train.iloc[:train_len]
valid_df = train.iloc[train_len:]
print(train_df.shape, valid_df.shape)

# Custom collect function to wrap sound features

def collate_fn_wrap(batch):
    '''
    wraps batch of variable length
    '''
    
    ## get sequence lengths
    lengths = [t['features'].shape[1] for t in batch]
    maxlen = max(lengths)
    
    for i in range(len(batch)):
        batch[i]['features'] = torch.from_numpy(batch[i]['features'])
        k = math.ceil(maxlen/lengths[i])
        batch[i]['features'] = batch[i]['features'].repeat(1, k)[:, :maxlen]
        # assert batch[i]['features'].shape[1] == maxlen
        
    labels = torch.tensor([i['label'] for i in batch])
    features = torch.stack([i['features'] for i in batch])
    return {'features':features, 'labels':labels}

# prepare data loaders
train_loader = torch.utils.data.DataLoader(BirdSoundDataset(train_df),
                                           batch_size=batch_size, 
                                           num_workers=4, 
                                           shuffle=True, 
                                           collate_fn=collate_fn_wrap,
                                           drop_last = True)

valid_loader = torch.utils.data.DataLoader(BirdSoundDataset(valid_df), 
                                           batch_size=batch_size, 
                                           num_workers=4, 
                                           shuffle=False, 
                                           collate_fn=collate_fn_wrap,
                                           drop_last = True)

print(len(train_loader), len(valid_loader)) 

'''
Modèle
'''

class BirdModel(nn.Module):
    
    def __init__(self, outdim=len(classes)):
        super(BirdModel, self).__init__()
        
        self.conv1 = torch.nn.Conv2d(1, 32, (16, 8), 
                                    stride=(16, 8),
                                    padding=0, 
                                    dilation=1,
                                    groups=1, 
                                    bias=True, 
                                    padding_mode='zeros')
    
        self.conv2 = torch.nn.Conv2d(32, 256, (8, 16), 
                                    stride=(1, 16),
                                    padding=0, 
                                    dilation=1,
                                    groups=1, 
                                    bias=True, 
                                    padding_mode='zeros')
        
        self.lstm = torch.nn.LSTM(input_size=256,
                                  hidden_size=256,
                                  num_layers=2, 
                                  dropout=0.2,
                                  bidirectional=True)
        
        self.fc = nn.Linear(4*256+128, outdim)
        self.drop = nn.Dropout(p=0.2)
        
    def forward(self, input):
        
        avg_features = torch.mean(input, dim=2)
        
        x = self.conv1(input.unsqueeze(1))
        x = self.conv2(x)
        x = x.squeeze(2).permute(2, 0, 1)
        
        _ , (hn, _) =  self.lstm(x)
        hn =  hn.permute(1, 0, 2).reshape(hn.shape[1], -1)
        
        x = torch.cat((hn, avg_features), dim=1)
        return self.fc(self.drop(x))





model = BirdModel()
print(model.to(device))

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

def mixup_data(x, y, alpha=1.0, use_cuda=True):

    '''Compute the mixup data. Return mixed inputs, pairs of targets, and lambda'''
    if alpha > 0.:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1.
    batch_size = x.size()[0]
    if use_cuda:
        index = torch.randperm(batch_size).cuda()
    else:
        index = torch.randperm(batch_size)

    mixed_x = lam * x + (1 - lam) * x[index,:]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

def mixup_criterion(y_a, y_b, lam):
    return lambda criterion, pred: lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

# number of epochs to train the model
n_epochs = 20

valid_loss_min = np.Inf # track change in validation loss

print('first')
print(torch.cuda.device_count())
print('last')

for epoch in range(1, n_epochs+1):

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0
    
    scheduler.step()
    
    ###################
    # train the model #
    ###################
    model.train()
    
    bar = tqdm(train_loader, total=len(train_loader), leave=False)
    for data in bar:
        
        features = data['features'].to(device)
        target = data['labels'].to(device)
        
        optimizer.zero_grad()
        
        inputs, targets_a, targets_b, lam = mixup_data(features, target, 0.2, use_cuda=torch.cuda.is_available())
        outputs = model(inputs)
        loss_func = mixup_criterion(targets_a, targets_b, lam)
        loss = loss_func(criterion, outputs)
        
        loss.backward()
        
        optimizer.step()
        
        bar.set_postfix({'loss': loss.item()})
        train_loss += loss.item()*features.size(0)
        
    ######################    
    # validate the model #
    ######################
    with torch.no_grad():
        targets = []
        preds = []
        model.eval()
        bar = tqdm(valid_loader, total=len(valid_loader), leave=False)
        for data in bar:
            features = data['features'].to(device)
            target = data['labels'].to(device)
            
            output = model(features)
            loss = criterion(output, target)
            
            pred = torch.argmax(output, dim=1)
            
            targets.extend(target.cpu().detach().numpy().tolist())
            preds.extend(pred.cpu().detach().numpy().tolist())
            
            # update average validation loss
            valid_loss += loss.item()*features.size(0)
    
    acc = np.sum(np.array(preds) == np.array(targets)) / len(preds)
    
    # calculate average losses
    train_loss = train_loss/len(train_loader.dataset)
    valid_loss = valid_loss/len(valid_loader.dataset)
        
    # print training/validation statistics 
    print('Epoch: {} \tValidation Acc: {:.6f}'.format(epoch, acc))
    print('Training Loss: {:.6f} \tValidation Loss: {:.6f}'.format(train_loss, valid_loss))
    
    # save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model.state_dict(), 'model_VF0.3.pt')
        valid_loss_min = valid_loss

print(preds[:5], targets[:5])

from sklearn.metrics import classification_report

print(classification_report(targets, preds))

from sklearn.metrics import confusion_matrix

print(confusion_matrix(targets, preds))

