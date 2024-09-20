import torch
from torch.autograd import Variable
import math
from backports import lzma
import os
import getdata
from torch.utils.data import DataLoader

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def getFileSize_KB(filePath):
    fsize = os.path.getsize(filePath)	# 返回的是字节大小
    return round(fsize / 1024, 2)

def cal_sum_big(shapeList):
    sum = 1
    if len(shapeList) == 0:
        # print('yes 0')
        return 0
    for num in shapeList:
        # print(num)
        sum = sum * num
    return sum
magic_num = 0.0005
def cal_delta(a, b):
    c = (a - b) / (2 * math.log(1 + magic_num)) + 0.5
    c = torch.floor(c)
    d = c.clone().type(torch.int)
    return d

# model1: target_model
# model2: old_model
def cal_ssim(model1_path, model2_path, diff_path):

    model1 = torch.load(model1_path)
    model2 = torch.load(model2_path)
    weights1 = model1.state_dict()
    weights2 = model2.state_dict()
    weight_key = list(weights1.keys())
    
    tensor_dict = {}
    for key in weight_key:
        if not weights1[key].shape == weights2[key].shape:
            tensor_dict[key] = Variable(weights1[key])
            continue
        img1 = Variable(weights1[key])
        img2 = Variable(weights2[key])
        # 计算同一个层两个模型的差分
        tensor_dict[key] = cal_delta(img1, img2)
    torch.save(tensor_dict, diff_path)

def cal_ssim_with_ignore(model1, model2, diff_path, ignore_dict):
    weights1 = model1.state_dict()
    weights2 = model2.state_dict()
    weight_key = list(weights1.keys())
    
    tensor_dict = {}
    # print(ignore_dict.keys())
    for key in weight_key:
        if not weights1[key].shape == weights2[key].shape:
            tensor_dict[key] = Variable(weights1[key])
            continue
        flag = 0
        
        for ignore_key in ignore_dict.keys():
            if ignore_key in key:
                # print(f"Yes no use, {ignore_key}")
                flag = 1
                break
        if flag == 1:
            continue
        img1 = Variable(weights1[key])
        img2 = Variable(weights2[key])
        # 计算同一个层两个模型的差分
        tensor_dict[key] = cal_delta(img1, img2)
    torch.save(tensor_dict, diff_path)


def compress(diff_path, compress_path):
    pf = open(compress_path, 'wb')
    data = open(diff_path,'rb').read()  # 简化描述未关文件
    data_comp = lzma.compress(data) # 压缩数据
    pf.write(data_comp)  # 写文件
    pf.close()  # 关闭
    return getFileSize_KB(compress_path)


def resume_tensor(delta_tensor, base_tensor):
    ans = 2 * delta_tensor * math.log(1 + magic_num) + base_tensor
    return ans

def resume_model(diff_path, previous_model_path, new_model_path, new_class_num):
    delta_dict = torch.load(diff_path)
    previous_model = torch.load(previous_model_path)
    previous_model_dict = previous_model.state_dict()
    new_model = torch.load(previous_model_path)
    num_fc = new_model.classifier[3].in_features
    new_model.classifier[3] = torch.nn.Linear(in_features=num_fc, out_features=new_class_num)
    
    for key in delta_dict.keys():
        if not delta_dict[key].shape == previous_model_dict[key].shape:
            previous_model_dict[key] = delta_dict[key]
            # print(f'shape = {previous_model_dict[key].shape}')
        else:
            previous_model_dict[key] = resume_tensor(delta_dict[key], previous_model_dict[key])
    new_model.load_state_dict(previous_model_dict)
    torch.save(new_model, new_model_path)

def test_acc(data_path, model_path):
    test_batch_size = 32
    test_dataset = getdata.ImageClassificationDataset(data_path + '/' + 'val')
    test_loader = DataLoader(test_dataset, batch_size=test_batch_size, shuffle=True,num_workers=4)
    
    model = torch.load(model_path)
    model = model.to(device)
    model.eval()
    best_acc = 0
    with torch.no_grad():
        correct = 0
        total = 0
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            output = model(images)
            _, predicted = torch.max(output.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        print('Test Accuracy  {} %'.format(100*(correct/total)))
        if correct / total > best_acc:
            best_acc = correct / total
    return best_acc

if __name__ == '__main__':
    print('test_deltadnn')
    diff_path = './model_zoo/diff_pkg/dog_cat_for_dog.pth'

    # 做差分
    # model1 = '/root/code/to_xuwf2/model_pth_mobileNet/multiple_classes_model_cat_dog_home/MobileNetv2_cat_dog_home_3class.pth'
    # model2 = '/root/code/to_xuwf2/model_pth_mobileNet/multiple_classes_model_dog_home/MobileNetv2_dog_home_2class.pth'
    # cal_ssim(model1, model2, diff_path)

    # 还原差分
    # previous_model_path = './model_zoo/now_models/MobileNetv2_dog_home_2class.pth'
    new_model_path = './model_zoo/now_models/MobileNetv2_cat_dog_home_3class.pth'
    # resume_model(diff_path, previous_model_path, new_model_path, 3)

    # 测试准确率
    test_acc('/root/code/to_xuwf2/datasets_new_data/dataset_cat_dog_CL', new_model_path)
    

    

    



    

