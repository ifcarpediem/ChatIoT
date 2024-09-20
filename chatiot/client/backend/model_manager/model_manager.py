import torch
from torch.autograd import Variable
import math
from torchvision import models
import json
import os
import copy
import requests
import time
import backend.model_manager.ddpg_to_use as ddpg_to_use
import backend.model_manager.sqlite_models as sqlite_models
from config import CONFIG

# 首先获取需求的单分类model
# 在本地决策需要合并的分类
# 请求新的分类model
# 下载到本地
# 删除原来的model

def get_json(json_path):
    with open(json_path,'r',encoding='utf8')as fp:
        json_data = json.load(fp)
        return json_data
def transfer_to_list(name_str):
    a = copy.deepcopy(name_str)
    a = a.replace('\'', '\"')
    list_str = json.loads(a)
    return list_str

def delete_model(id):
    sqlite_models.delete_model(id)

def get_model_name(id):
    return sqlite_models.get_model_name_by_id(id)

def get_name_list_from_id12(id1, id2):
    model1 = sqlite_models.get_model_massage_by_id(id1)
    model2 = sqlite_models.get_model_massage_by_id(id2)
    name_str1 = model1[5]
    name_str2 = model2[5]
    name_list1 = transfer_to_list(name_str1)
    name_list2 = transfer_to_list(name_str2)
    return name_list1 + name_list2

def request_model_RL(good_name_list):
    id1, id2 = model_merge_decision()
    res_dict = {}
    if id1 == -1:
        new_model_id = request_model(good_name_list)
        res_dict['merge'] = False
        res_dict['model_id'] = [new_model_id]
    else:
        new_model_id1 = request_model(good_name_list)
        name_list = get_name_list_from_id12(id1, id2)
        new_model_id2 = request_model(name_list)
        res_dict['merge'] = True
        res_dict['delete_id'] = [id1, id2]
        sqlite_models.delete_model(id1)
        sqlite_models.delete_model(id2)
        res_dict['model_id'] = [new_model_id1, new_model_id2]
    return json.dumps(res_dict, ensure_ascii=False)
        
def request_model(good_name_list):
    print('云端模型蒸馏中......')
    time.sleep(1)
    request_yolo_model_file(good_name_list)
    res_json = request_yolo_model_massage(good_name_list)
    model_id = sqlite_models.add_model_json(res_json)  
    return model_id

def request_yolo_model(good_name_list):

    request_yolo_model_file(good_name_list)

    res_json = request_model_massage(good_name_list)
    model_id = sqlite_models.add_model_json(res_json)
    # print(sqlite_models.get_all_models())
    # print(f'model_id = {model_id}')
    return model_id

def get_model_massage_by_id(model_id):
    return sqlite_models.get_model_name_by_id(model_id)

def get_all_models():
    return sqlite_models.get_all_models()
    
def request_model_massage(good_name_list):
    name_list = copy.deepcopy(good_name_list)
    request_classes = '_'.join(name_list)
    model_server_host = CONFIG.configs['model_server']['host']
    model_server_port = CONFIG.configs['model_server']['port']
    url_file = f'http://{model_server_host}:{model_server_port}/download_massage/' + request_classes
    response = requests.get(url_file)
    res_json = response.json()
    # print(res_json['model_accuracy'])
    return res_json
def request_yolo_model_massage(good_name_list):
    name_list = copy.deepcopy(good_name_list)
    request_classes = '_'.join(name_list)
    model_server_host = CONFIG.configs['model_server']['host']
    model_server_port = CONFIG.configs['model_server']['port']
    url_file = f'http://{model_server_host}:{model_server_port}/download_yolo_massage/' + request_classes
    response = requests.get(url_file)
    res_json = response.json()
    # print(res_json['model_accuracy'])
    return res_json
    
    
# 获取一个model
def request_model_file(good_name_list):
    name_list = copy.deepcopy(good_name_list)
    request_classes = '_'.join(name_list)
    model_server_host = CONFIG.configs['model_server']['host']
    model_server_port = CONFIG.configs['model_server']['port']
    url_file = f'http://{model_server_host}:{model_server_port}/download_multi/' + request_classes
    print(request_classes)

    name_list.append('home')
    name_list.sort()
    model_save_path = './model_manager/model_zoo/' + 'MobileNetv2_' + '_'.join(name_list) +'_' + str(len(name_list)) +'class.pth'

    # start_time = time.time()
    File = requests.get(url_file, stream=True,timeout=(1200, 1200))
    with open(model_save_path,'wb+') as f:
        # 分块写入文件
        for chunk in File.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    f.close()
    # end_time = time.time()
    # print(end_time - start_time)
    return model_save_path

# 获取一个yolo_model
def request_yolo_model_file(good_name_list):
    name_list = copy.deepcopy(good_name_list)
    request_classes = '_'.join(name_list)
    model_server_host = CONFIG.configs['model_server']['host']
    model_server_port = CONFIG.configs['model_server']['port']
    url_file = f'http://{model_server_host}:{model_server_port}/download_yolo/' + request_classes
    # print(request_classes)

    # name_list.append('home')
    # name_list.sort()
    model_save_path = './model_manager/yolo_model_zoo/' + request_classes + '.pt'

    # start_time = time.time()
    File = requests.get(url_file, stream=True,timeout=(1200, 1200))
    content_size = int(File.headers['content-length']) # 内容体总大小
    chunk_size=1024
    size = 0  # 初始化已下载大小
    
    print('开始下载,[文件大小]:{size:.2f} MB'.format(
                size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
    time.sleep(1)
    with open(model_save_path,'wb+') as f:
        # 分块写入文件
        for chunk in File.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                size += len(chunk)
                print('\r' + '[下载进度]:%s%.2f%%' % (
                    '>' * int(size * 50 / content_size), float(size / content_size * 100)), end=' ')
    print('\n模型部署成功！')
                
    f.close()
    
    return model_save_path

class_to_num_28 = {'people': 0, 'cat': 1, 'dog': 2, 'child': 3, 'bird': 4, 'Courier': 5, 'Wine bottles': 6, 'remote control': 7, 'glasses': 8, 'laptop': 9, 'reading': 10, 'eating': 11, 'run': 12, 'dance': 13, 'Sweeping': 14, 'cooking': 15, 'snake': 16, 'chicken': 17, 'mouse': 18, 'pig': 19, 'rabbit': 20, 'turtle': 21, 'toy': 22, 'food': 23, 'fruit': 24, 'flower': 25, 'dumbbell': 26, 'clothes': 27}
def get_name_from_model(model):
    a = copy.deepcopy(model[5])
    a = a.replace('\'', '\"')
    list_str = json.loads(a)
    # print(list_str[0])
    # return list_str[0]
    num_of_name = ddpg_to_use.after_class_30[class_to_num_28[list_str[0]]]
    return list_str, num_of_name
def get_state_from_database():
    all_models = sqlite_models.get_all_models()
    all_models_pro = []
    for model in all_models:
        list_str, num_of_name = get_name_from_model(model)
        tmp_list = [model[4], model[2], num_of_name, list_str, model[0]]
        all_models_pro.append(tmp_list)
    return all_models_pro
     
# get all model pro in database
# 决策：哪两个模型合并
# 获取那个合并了的模型
def model_merge_decision():
    ddpg = ddpg_to_use.DDPG_USE()
    ddpg.all_models_pro = get_state_from_database()
    num1, num2 = ddpg.choose_action_jet(10)
    return num1, num2

def merge_models(id1, id2, new_model_name_list):
    sqlite_models.delete_model(id1)
    sqlite_models.delete_model(id2)

 
if __name__ == '__main__':
    request_model(['pig','cat'])
    
    