import torch.nn as nn
import torch.nn.functional as F

# ResidualBlock : vanish gradient 방지
class ResidualBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion * planes)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.dropout(out, p=0.2, training=self.training)
        out = F.relu(out)
        return out


class Model(nn.Module):
    def __init__(self, num_classes):
        super(Model, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(32)
        self.module1 = ResidualBlock(32, 32, stride=1)
        self.module2 = ResidualBlock(32, 64, stride=2)
        self.module3 = ResidualBlock(64, 128, stride=2)
        self.module4 = ResidualBlock(128, 256, stride=2)

        self.linear = nn.Linear(256, num_classes)

    def forward(self, input):
        x = F.relu(self.bn1(self.conv1(input)))
        x = self.module1(x)
        x = self.module2(x)
        x = self.module3(x)
        x = self.module4(x)
        x = F.avg_pool2d(x, 4)
        x = x.view((x.shape[0], -1))
        x = self.linear(x)
        return x
