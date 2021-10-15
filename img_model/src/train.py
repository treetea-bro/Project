import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import model
import csv
from PIL import Image
from torchvision.transforms import ToTensor
from torch.utils.data import DataLoader
import os
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sn
import pandas as pd

# cuda를 사용할 수 없을때 summary를 import한다.
if not torch.cuda.is_available():
    from torchsummary import summary

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')  # gpu를 사용할 수 있으면 사용한다.

shape = (44, 44)  # crop, summary부분에서 사용한다.


# data 전처리 클래스
class DataSetFactory:
    def __init__(self):
        images = []  # Training 이미지 담을 배열
        emotions = []  # Training 라벨 담을 배열
        private_images = []  # private_test 이미지 담을 배열
        private_emotions = []  # private_test 라벨 담을 배열
        public_images = []  # public_test 이미지 담을 배열
        public_emotions = []  # public_test 라벨 담을 배열

        # kaggle에서 다운받은 이미지관련 data를 전처리해서 각 배열들에 담는다.
        with open('../dataset/icml_face_data.csv', 'r') as csvin:
            data = csv.reader(csvin)  # 경로에서 csv파일 읽어들인다.
            next(data)  # 헤더(컬럼)정보를 빼낸다.
            for row in data:
                # kaggle data 전처리 과정
                face = [int(pixel) for pixel in row[2].split()]
                face = np.asarray(face).reshape(48, 48)
                face = face.astype('uint8')
                if row[0] not in ["1", "2"]: # 기존 Disgust, Fear
                    if row[0] == '5': # 기존 Surprise
                            row[0] = '1'
                    if row[0] == '6': # 기존 Neutral
                        row[0] = '2'
                    # 데이터 유형에따라 training배열에 넣을지, test배열에 넣을지 골라서 넣어준다.
                    if row[1] == 'Training':                        
                        emotions.append(int(row[0]))
                        images.append(Image.fromarray(face))
                    elif row[1] == "PrivateTest":
                        private_emotions.append(int(row[0]))
                        private_images.append(Image.fromarray(face))
                    elif row[1] == "PublicTest":
                        public_emotions.append(int(row[0]))
                        public_images.append(Image.fromarray(face))

        # 크롤링한 데이터(당황 클래스)를 전처리하고 라벨과 이미지를 모든 배열에 넣어준다.
        emb_path = "../dataset/당황한표정"
        for filename in os.listdir(emb_path):
            img = Image.open(os.path.join(emb_path, filename)).convert("L")
            resized = img.resize((48, 48))
            emotions.append(1)
            images.append(resized)
            private_emotions.append(1)
            private_images.append(resized)
            public_emotions.append(1)
            public_images.append(resized)

        # 각 데이터의 사이즈를 확인한다.
        print('training size %d : private val size %d : public val size %d' % (
            len(images), len(private_images), len(public_images)))

        # train 이미지의 transform 형식을 정해준다.
        train_transform = transforms.Compose([
            transforms.RandomCrop(shape[0]),  # 전역변수로 선언한 44크기로 randomCrop한다.
            transforms.RandomHorizontalFlip(),  # 50%의 확률로 좌우반전 시킨다.
            ToTensor(),
        ])

        # 각 test 이미지의 transform 형식을 정해준다.
        val_transform = transforms.Compose([
            transforms.CenterCrop(shape[0]),  # 44크기로 CenterCrop한다.
            ToTensor(),
        ])

        # 각 데이터에 맞는 transform과 image, label을 가지고 DataSet에 넣어주고 객체를 리턴받아 저장한다.
        self.training = DataSet(transform=train_transform, images=images, emotions=emotions)
        self.private = DataSet(transform=val_transform, images=private_images, emotions=private_emotions)
        self.public = DataSet(transform=val_transform, images=public_images, emotions=public_emotions)


# DataLoader에서 transform, image, label을 사용 할 수 있게 한다.
class DataSet(torch.utils.data.Dataset):
    def __init__(self, transform=None, images=None, emotions=None):
        self.transform = transform
        self.images = images
        self.emotions = emotions

    def __getitem__(self, index):
        image = self.images[index]
        emotion = self.emotions[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, emotion

    def __len__(self):
        return len(self.images)


def main():
    # variables  -------------
    batch_size = 128
    lr = 0.01  # learning late
    epochs = 300
    learning_rate_decay_start = 80  # learning late 감소 지점
    learning_rate_decay_every = 5  # learning late 속도 조절 관련 변수
    learning_rate_decay_rate = 0.9  # learning late 속도 조절 관련 변수
    # ------------------------

    classes = ['Angry', 'Embarrassment', 'Neutral', 'Happy', 'Sad']
    network = model.Model(num_classes=len(classes)).to(device)  # 모델에 classes 길이를 넣어서 객체 생성

    # cuda가 사용 불가능하면 summary를 출력한다.
    # if not torch.cuda.is_available():
    #     summary(network, (1, shape[0], shape[1]))

    optimizer = torch.optim.SGD(network.parameters(), lr=lr, momentum=0.9, weight_decay=5e-3)
    criterion = nn.CrossEntropyLoss()
    factory = DataSetFactory()  # 데이터를 가지고 전처리 후, DataLoader에서 사용할 수 있게까지 준비해놓은 클래스

    # DataSetFactory에서 준비된 data를 가지고 각각 용도에 맞게 DataLoader에 넣어서 batch를 이용해 묶어준다.
    training_loader = DataLoader(factory.training, batch_size=batch_size, shuffle=True)
    validation_loader = {
        'private': DataLoader(factory.private, batch_size=batch_size),
        'public': DataLoader(factory.public, batch_size=batch_size)
    }

    min_validation_loss = {
        'private': 10000,
        'public': 10000,
    }

    for epoch in range(epochs):
        # training
        network.train()
        total = 0
        correct = 0
        total_train_loss = 0

        # epoch가 거듭될수록 learning rate를 더 낮춰준다.
        if epoch > learning_rate_decay_start >= 0:
            frac = (epoch - learning_rate_decay_start) // learning_rate_decay_every
            decay_factor = learning_rate_decay_rate ** frac
            current_lr = lr * decay_factor
            for group in optimizer.param_groups:
                group['lr'] = current_lr
        #else:
            #current_lr = lr

        #print('learning_rate: %s' % str(current_lr))

        # 각 epoch마다 Training Loss를 구하고, Accuracy를 찍는다.
        for i, (x_train, y_train) in enumerate(training_loader):
            optimizer.zero_grad()
            x_train = x_train.to(device)
            y_train = y_train.to(device)
            y_predicted = network(x_train)
            loss = criterion(y_predicted, y_train)
            loss.backward()
            optimizer.step()
            _, predicted = torch.max(y_predicted.data, 1)
            total_train_loss += loss.data
            total += y_train.size(0)
            correct += predicted.eq(y_train.data).sum()
        accuracy = 100. * float(correct) / total
        print('Epoch [%d/%d] Training Loss: %.4f, Accuracy: %.4f' % (
            epoch + 1, epochs, total_train_loss / (i + 1), accuracy))

        # validation test
        network.eval()
        with torch.no_grad():
            for name in ['private', 'public']:
                total = 0
                correct = 0
                total_validation_loss = 0

                # 각 epoch마다 validation Loss를 구하고, Accuracy를 찍는다.
                for j, (x_val, y_val) in enumerate(validation_loader[name]):
                    x_val = x_val.to(device)
                    y_val = y_val.to(device)
                    y_val_predicted = network(x_val)
                    val_loss = criterion(y_val_predicted, y_val)
                    _, predicted = torch.max(y_val_predicted.data, 1)
                    total_validation_loss += val_loss.data
                    total += y_val.size(0)
                    correct += predicted.eq(y_val.data).sum()
                accuracy = 100. * float(correct) / total
                
                # 전의 epoch의 loss보다 현재 epoch의 loss가 낮을경우 save해준다.
                if total_validation_loss < min_validation_loss[name]:
                    if epoch >= 10:
                        print('saving new model')
                        state = {'net': network.state_dict()}
                        torch.save(state, '../trained/%s_model_%d_%d.t7' % (name, epoch + 1, accuracy))
                    min_validation_loss[name] = total_validation_loss

                print('Epoch [%d/%d] %s validation Loss: %.4f, Accuracy: %.4f' % (
                    epoch + 1, epochs, name, total_validation_loss / (j + 1), accuracy))


if __name__ == "__main__":
    main()
