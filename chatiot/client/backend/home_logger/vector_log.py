from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import json
import linecache
from sentence_transformers.util import cos_sim
from sentence_transformers import SentenceTransformer

def get_embeddings2(sentences):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    ans = model.encode(sentences)
    return ans

def get_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:  
    # 使用json.load()方法解析JSON数据  
        data = json.load(file)
    return data

def add_data(embeddings_dict, json_path):
     with open(json_path,"w") as f:
        json.dump(embeddings_dict,f)
        print("数据添加完成...")

def get_ind(embeddings_dict):
    ind = 0
    if not (embeddings_dict == {}):
        ind = len(embeddings_dict)
    return ind

def get_all_cosine_similarity(sentences, json_path):
    sentence_embeddings = get_embeddings2(sentences)
    vector_dict = get_json(json_path)
    similarity_list = []
    for kk in vector_dict.keys():
        now_embedding = vector_dict[kk]
        # service_similarity = F.cosine_similarity(torch.tensor(sentence_embeddings[0]).unsqueeze(0), torch.tensor(now_embedding).unsqueeze(0)).item()
        service_similarity = cos_sim(sentence_embeddings, now_embedding)
        similarity_list.append(service_similarity)
    return similarity_list

def search_with_range(sentences, json_path, txt_path, threshold=0):
    similarity_list = get_all_cosine_similarity(sentences, json_path)
    ans = []
    # print(f'sen = {sentences}')
    print(f'similarity_list = {similarity_list}')
    
    for i in range(len(similarity_list)):
        if similarity_list[i] > threshold:
            # print(f'i = {i}')
            linecache.clearcache()
            text = linecache.getline(txt_path, i + 1)
            ans.append(text)
    return ans

def search_message(sentences, threshold=0.5):
    json_path = './memory/vector.json'
    txt_path = './memory/sentence.txt'
    return search_with_range(sentences, json_path, txt_path, threshold)


# 时间 地点 人物 事件
def add_sentence(sentences, json_path, txt_path):
    # sentences = [date_time + ' ' + place + ' ' + who + '' + event]
    embeddings_dict = get_json(json_path)
    sentence_embeddings = get_embeddings2(sentences)
    # 写入txt
    with open(txt_path, 'a') as f:
        for ll in sentences:
            f.write(ll + '\n')

    ind = get_ind(embeddings_dict)
    for ll in sentence_embeddings.tolist():
        embeddings_dict[ind] = ll
        # print(len(ll))
        ind = ind + 1
    add_data(embeddings_dict, json_path)

def add_message(sentences):
    json_path = './memory/vector.json'
    txt_path = './memory/sentence.txt'
    add_sentence(sentences, json_path, txt_path)
    return '添加成功！'



