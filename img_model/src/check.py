import cv2
import matplotlib.cm as cm
import numpy as np
import torch.hub
import os
from . import model
from PIL import Image
from torchvision import transforms
from torchsummary import summary
from .visualize.grad_cam import BackPropagation, GradCAM, GuidedBackPropagation

# haarcascade_frontalface_default.xml
faceCascade = cv2.CascadeClassifier('Final_Proeject\\img_model\\src\\visualize\\haarcascade_frontalface_alt2.xml')
shape = (48, 48)  # 전처리 할 이미지 크기
classes = ['Angry', 'Embarrassment', 'Neutral', 'Happy', 'Sad']

# 이미지 전처리
def preprocess(image_path):
    transform_test = transforms.Compose([
        transforms.ToTensor()
    ])
    image = cv2.imread(image_path)  # 이미지를 ndarray로 읽어온다음
    # 이미지에서 사람얼굴이 있는지 찾아본 후
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(1, 1),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    # 이미지에서 사람얼굴이 없으면 이미지 사이즈를 resize하고,
    if len(faces) == 0:
        #print('no face found')
        face = cv2.resize(image, shape)
    else:
    # 사람 얼굴이 존재하면 해당 얼굴부분만 잘라내서 resize해서
        (x, y, w, h) = faces[0]
        face = image[y:y + h, x:x + w]
        face = cv2.resize(face, shape)

    # 이미지에 transform을 적용한 값과 이미지를 리턴한다.
    img = Image.fromarray(face).convert('L')
    inputs = transform_test(img)
    return inputs, face


def get_gradient_image(gradient):
    gradient = gradient.cpu().numpy().transpose(1, 2, 0)
    gradient -= gradient.min()
    gradient /= gradient.max()
    gradient *= 255.0
    return np.uint8(gradient)


def get_gradcam_image(gcam, raw_image, paper_cmap=False):
    gcam = gcam.cpu().numpy()
    cmap = cm.jet_r(gcam)[..., :3] * 255.0
    if paper_cmap:
        alpha = gcam[..., None]
        gcam = alpha * cmap + (1 - alpha) * raw_image
    else:
        gcam = (cmap.astype(np.float64) + raw_image.astype(np.float64)) / 2
    return np.uint8(gcam)


def guided_backprop(images, model_name):
    # 이미지를 전처리해서 images의 딕셔너리에 추가한다.
    for image in images:
        target, raw_image = preprocess(image['path'])
        image['image'] = target
        image['raw_image'] = raw_image

    net = model.Model(num_classes=len(classes))
    # 기존에 save한 모델을 load한다.
    checkpoint = torch.load(os.path.join('Final_Proeject\\img_model\\trained', model_name), map_location=torch.device('cpu'))
    net.load_state_dict(checkpoint['net'])
    net.eval()
    #summary(net, (1, shape[0], shape[1]))

    # 테스트 결과 이미지를 생성한다.
    result_images = []
    for image in images:
        img = torch.stack([image['image']])
        bp = BackPropagation(model=net)
        probs, ids = bp.forward(img)
        gcam = GradCAM(model=net)
        _ = gcam.forward(img)

        gbp = GuidedBackPropagation(model=net)
        _ = gbp.forward(img)

        # Guided Backpropagation
        actual_emotion = ids[:, 0]
        gbp.backward(ids=actual_emotion.reshape(1, 1))
        gradients = gbp.generate()

        # Grad-CAM
        gcam.backward(ids=actual_emotion.reshape(1, 1))
        regions = gcam.generate(target_layer='module4')

        # Get Images
        label_image = np.zeros((shape[0], 65, 3), np.uint8)
        cv2.putText(label_image, classes[actual_emotion.data], (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255),
                    1, cv2.LINE_AA)

        prob_image = np.zeros((shape[0], 60, 3), np.uint8)
        cv2.putText(prob_image, '%.1f%%' % (probs.data[:, 0] * 100), (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1, cv2.LINE_AA)

        guided_bpg_image = get_gradient_image(gradients[0])
        guided_bpg_image = cv2.merge((guided_bpg_image, guided_bpg_image, guided_bpg_image))

        grad_cam_image = get_gradcam_image(gcam=regions[0, 0], raw_image=image['raw_image'])

        guided_gradcam_image = get_gradient_image(torch.mul(regions, gradients)[0])
        guided_gradcam_image = cv2.merge((guided_gradcam_image, guided_gradcam_image, guided_gradcam_image))

        img = cv2.hconcat(
            [image['raw_image'], label_image, prob_image, guided_bpg_image, grad_cam_image, guided_gradcam_image])
        result_images.append(img)
        print(image['path'], classes[actual_emotion.data], probs.data[:, 0] * 100)
    cv2.imwrite('Final_Proeject\\guided_gradcam.jpg', cv2.resize(cv2.vconcat(result_images), None, fx=2, fy=2))


def model_load(model_name):
    global net
    net = model.Model(num_classes=len(classes))
    # 기존에 save한 모델을 load한다.
    checkpoint = torch.load(os.path.join('Final_Proeject\\static\\models', model_name), map_location=torch.device('cpu'))
    net.load_state_dict(checkpoint['net'])
    net.eval()

def concat_info(image):
    global net
    target, _ = preprocess(image)

    img = torch.stack([target])
    bp = BackPropagation(model=net)
    probs, ids = bp.forward(img)
    return classes[ids[:, 0].data], "%0.2f"%(probs.data[:, 0] * 100).item()

def main():
    guided_backprop(
        # images 안에 딕셔너리 형태로 키=path, 밸류=이미지경로로 테스트 할 이미지를 지정해준다. (딕셔너리 하나당 key,value 하나)
        images=[
            {'path': '../test/a_resized_1.png'},
            {'path': '../test/a_resized_2.png'},
            {'path': '../test/a_resized_3.png'},
            {'path': '../test/a_resized_4.png'},
            {'path': '../test/a_resized_5.png'},
        ],
        # train에서 학습시키고 save한 모델명을 적는다. (traind 폴더에 있음)
        model_name='private_model_266_67.t7'
    )


if __name__ == "__main__":
    main()
