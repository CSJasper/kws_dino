import torch
import torch.nn as nn
import torch.cuda as cuda
import torchvision.models as models
import librosa
import numpy as np


def load_on_memory():
    device = 'cuda' if cuda.is_available() else 'cpu'

    model = models.resnet18()
    num_features = model.fc.in_features
    model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
    model.fc = nn.Linear(in_features=num_features, out_features=4)
    model_state_path = ''

    model.load_state_dict(torch.load(model_state_path))
    model.eval()

    return model


def detect(wav_file_path: str, model: nn.Module):
    sig, sr = librosa.load(wav_file_path, sr=16000)

    if sr < len(sig):
        sig = sig[:sr]
    elif sr > len(sig):
        sig = np.pad(sig, (0, sr - len(sig)), 'constant')

    spec_wav = librosa.stft(sig, n_fft=640, hop_length=320, win_length=640, center=False)
    power_spec = np.abs(spec_wav) ** 2
    mel_spec = librosa.feature.melspectrogram(S=power_spec, sr=sr, n_fft=640, hop_length=320, power=2.0)
    mel_spec = torch.FloatTensor(mel_spec)
    mel_spec = mel_spec.view(1, 1, mel_spec.shape[0], mel_spec.shape[1])

    return model(mel_spec)


def _detect(wav_file_path: str, model=None):
    from random import randint

    sig, sr= librosa.load(wav_file_path, sr=16000)

    if sr < len(sig):
        sig = sig[:sr]
    elif sr > len(sig):
        sig = np.pad(sig, (0, sr - len(sig)), 'constant')

    spec_wav = librosa.stft(sig, n_fft=640, hop_length=320, win_length=640, center=False)
    power_spec = np.abs(spec_wav) ** 2
    mel_spec = librosa.feature.melspectrogram(S=power_spec, sr=sr, n_fft=640, hop_length=320, power=2.0)
    mel_spec = torch.FloatTensor(mel_spec)
    mel_spec = mel_spec.view(1, mel_spec.shape[0], mel_spec.shape[1])

    return randint(0, 1) % 2 == 0


if __name__ == '__main__':
    import torchvision.models as models
    import time

    model = models.resnet18(pretrained=True)
    model.conv1 = nn.Conv2d(
        in_channels=1,
        out_channels=64,
        kernel_size=(7, 7),
        stride=(2, 2),
        padding=(3, 3),
        bias=False
    )
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(
        in_features=num_ftrs,
        out_features=10
    )
    model.eval()

    start_time = time.time()

    with torch.no_grad():
        detect('./test.wav', model)

    end_time = time.time()

    print(f'Execution time : {end_time - start_time}')


