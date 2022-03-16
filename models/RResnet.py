import torch.nn
import torch.nn as nn
import torch.cuda as cuda
import torchvision.models as models
import torchaudio

class rresnet(nn.Module):
    def __init__(self,
                 in_features: int,
                 out_features: int):
        super(rresnet, self).__init__()

        pass

    def forward(self, x):
        out = self.rnn(x)
        out = self.resnet(out)
        return out


class resnet(models.resnet18):
    def __init__(self,
                 in_channel: int,
                 out_channel: int,
                 class_num: int):
        super(resnet, self).__init__()

        self.in_channel = in_channel
        self.out_channel = out_channel
        self.class_num = class_num

        self.resnet = models.resnet18(pretrained=True)
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, class_num)
        # do some kernel tweak
        self.resnet.conv1 = nn.Conv2d(in_channel=in_channel, out_channel=out_channel)


class DeepSpeech(torchaudio.)