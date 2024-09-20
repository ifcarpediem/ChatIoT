import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import copy
import math
import time
import json

########################## DDPG Framework ######################
class ActorNet(nn.Module): # define the network structure for actor and critic
    def __init__(self, s_dim, a_dim):
        super(ActorNet, self).__init__()
        self.fc1 = nn.Linear(s_dim, 30)
        self.fc1.weight.data.normal_(0, 0.1) # initialization of FC1
        self.out = nn.Linear(30, a_dim)
        self.out.weight.data.normal_(0, 0.1) # initilizaiton of OUT
    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.out(x)
        x = torch.tanh(x)
        # actions = 
        actions = (x + 1) * 392
        # actions = x * 2 # for the game "Pendulum-v0", action range is [-2, 2]
        return actions
class CriticNet(nn.Module):
    def __init__(self, s_dim, a_dim):
        super(CriticNet, self).__init__()
        self.fcs = nn.Linear(s_dim, 30)
        self.fcs.weight.data.normal_(0, 0.1)
        self.fca = nn.Linear(a_dim, 30)
        self.fca.weight.data.normal_(0, 0.1)
        self.out = nn.Linear(30, 1)
        self.out.weight.data.normal_(0, 0.1)
    def forward(self, s, a):
        x = self.fcs(s)
        y = self.fca(a)
        actions_value = self.out(F.relu(x+y))
        return actions_value
# who:要对谁做归一化，比如个数还是准确率还是类别
def do_min_max(models_list, who):
    min_num = 10000000
    max_num = -10000000
    res = copy.deepcopy(models_list)
    len_models = len(models_list)
    # print(models_list)
    for i in range(len_models):
        # print(f'mm = {models_list[i][who]}')
        if models_list[i][who] > max_num:
            max_num = models_list[i][who]
        if models_list[i][who] < min_num:
            min_num = models_list[i][who]
    if math.isclose(max_num, min_num, rel_tol=1e-3):
        for i in range(len_models):
            res[i][who] = 0
    else:
        for i in range(len_models):
            res[i][who] = (res[i][who] - min_num) / (max_num - min_num)
    return res
class_to_num_30 = {'people': 0, 'cat': 1, 'dog': 2, 'child': 3, 'bird': 4, 'Courier': 5, 'Wine bottles': 6, 'remote control': 7, 'glasses': 8, 'laptop': 9, 'reading': 10, 'eating': 11, 'run': 12, 'dance': 13, 'Sweeping': 14, 'cooking': 15, 'snake': 16, 'chicken': 17, 'mouse': 18, 'pig': 19, 'rabbit': 20, 'turtle': 21, 'toy': 22, 'food': 23, 'fruit': 24, 'flower': 25, 'dumbbell': 26, 'clothes': 27}
after_class_30 = [0, 1, 2, 3, 2, 0, 0, 0, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 0, 2, 0, 2]
def get_model_acc(name_list):
    return 0.987654321, '123'
class DDPG_USE():
    def __init__(self):
        self.actor_model = torch.load('./model_manager/actorNet.pth')
        self.all_models_pro = []
        self.acc_sum = 0
        self.n1 = 28
        self.n2 = 784
        self.avg_acc = 0
        self.obs_dim = 128
    def reset(self):
        self.all_models_pro = []
        self.acc_sum = 0
        self.n1 = 28
        self.n2 = 784
        self.avg_acc = 0
    def get_obs(self):
        # if not new_name == '_':
        #     self.add_new_model(new_name)
        tmp_all_models = copy.deepcopy(self.all_models_pro)
        
        # 个数归个数，准确率归准确率
        if len(tmp_all_models) > 1:
            print(f'len = {len(tmp_all_models)}')
            tmp_all_models = do_min_max(tmp_all_models, 0)
            tmp_all_models = do_min_max(tmp_all_models, 1)
            tmp_all_models = do_min_max(tmp_all_models, 2)
        res_obs = [0 for i in range(self.obs_dim)]
        res_obs[0] = len(self.all_models_pro) / 30
        idx = 1
        for lll in tmp_all_models:
            for i in range(3):
                res_obs[idx] = lll[i]
                idx = idx + 1
        return res_obs
    def find_another(self, num1):
        want_list = []
        min_num = 10000000
        id = 0
        for i in range(len(self.all_models_pro)):
            if i == num1:
                continue
            if self.all_models_pro[i][0] < min_num:
                min_num = self.all_models_pro[i][0]
                id = i
                want_list = copy.deepcopy(self.all_models_pro[i])
        return id
    def add_new_model(self, new_name):
        num_of_new_name = class_to_num_30[new_name]
        # pdata = ptt.get_p_data(num_of_new_name)
        # self.all_models.append([个数，准确率(，类别)])
        # new_add_list = [1, base_acc_list[class_to_num_dict[new_name]], ptt.predict(pdata)]
        # 这个tmpallmodels最后转化成obs的向量
        # self.all_models.append(copy.deepcopy(new_add_list))
        # new_add_list2 = [1, base_acc_list[class_to_num_dict[new_name]], ptt.predict(pdata), [new_name]]
        # new_add_list2 = [1, get_model_acc([new_name]), ptt.predict(pdata), [new_name]]
        model_acc, model_path = get_model_acc([new_name])
        self.acc_sum = self.acc_sum + model_acc
        new_add_list2 = [1, model_acc, after_class_30[num_of_new_name], [new_name], model_path]
        self.all_models_pro.append(copy.deepcopy(new_add_list2))
    def choose_action(self, up_num):
        # print(s)
        s = self.get_obs()
        s = torch.unsqueeze(torch.FloatTensor(s), 0)
        action_num = self.actor_model(s)[0].detach()
        action_num = np.clip(np.random.normal(action_num, 3), 0, 784)

        if len(self.all_models_pro) > up_num:
            
            num1 = int(action_num) % self.n2
            from_j = num1 % 30
            to_i = num1 // 30
            if from_j >= len(self.all_models_pro) or to_i >= len(self.all_models_pro):
                minnn1 = 10000
                minnn2 = 99999
                id1 = 0
                id2 = 0
                lenpro = len(self.all_models_pro)
                for i in range(lenpro):
                    pp = self.all_models_pro[i]
                    if pp[0] < minnn1:
                        minnn2 = minnn1
                        id2 = id1
                        id1 = i
                    elif pp[0] < minnn2:
                        minnn2 = pp[0]
                        id2 = i
                # print('Yeeeeeeeeeeeeeeeeee')
                # return self.get_obs(), 0, False, '_'
                num1, num2 = id1, id2
            else:
                num1, num2 = from_j, to_i
            if num1 == num2:
                    num2 = self.find_another(num1)
            name_list = []
            print(f'num1 = {num1}, num2 = {num2}')
            print(f'lenall = {len(self.all_models_pro)}, id1 = {len(self.all_models_pro[num1])},id2 = {len(self.all_models_pro[num2])}')
            for name in self.all_models_pro[num1][3]:
                name_list.append(name)
            for name in self.all_models_pro[num2][3]:
                name_list.append(name)

            previous_acc = (self.all_models_pro[num1][1] + self.all_models_pro[num2][1]) / 2
            self.acc_sum = self.acc_sum - self.all_models_pro[num1][1] * len(self.all_models_pro[num1][3]) - self.all_models_pro[num2][1] * len(self.all_models_pro[num2][3])

            tmpdel1 = copy.deepcopy(self.all_models_pro[num1])
            tmpdel2 = copy.deepcopy(self.all_models_pro[num2])
            # new_acc, _ = train_with_name_new_data.multiple_classes_model(name_list)
            new_acc = 90
            self.acc_sum = self.acc_sum + new_acc * len(name_list)
            # new_acc = self.cal_reward(self.all_models_pro[num1][4], self.all_models_pro[num2][4], self.all_models_pro[num1][1], self.all_models_pro[num2][1])
            new_add_list = [len(name_list), new_acc, copy.deepcopy(self.all_models_pro[num1][2]), copy.deepcopy(name_list)]

            # all_models_pro里面老的要删掉
            self.all_models_pro.remove(tmpdel1)
            self.all_models_pro.remove(tmpdel2)
            self.all_models_pro.append(copy.deepcopy(new_add_list))
    def add_new_model_jet(self, new_name):
        num_of_new_name = class_to_num_30[new_name]
        model_acc, model_path = get_model_acc([new_name])
        self.acc_sum = self.acc_sum + model_acc
        new_add_list2 = [1, model_acc, after_class_30[num_of_new_name], [new_name], model_path]
        self.all_models_pro.append(copy.deepcopy(new_add_list2))
        return num_of_new_name
    def choose_action_jet(self, up_num):
        # print(s)
        s = self.get_obs()
        s = torch.unsqueeze(torch.FloatTensor(s), 0)
        action_num = self.actor_model(s)[0].detach()
        # action_num = np.clip(np.random.normal(action_num, 3), 0, 784)

        if len(self.all_models_pro) > up_num:
            
            num1 = int(action_num) % self.n2
            from_j = num1 % 30
            to_i = num1 // 30
            if from_j >= len(self.all_models_pro) or to_i >= len(self.all_models_pro):
                minnn1 = 10000
                minnn2 = 99999
                id1 = 0
                id2 = 0
                lenpro = len(self.all_models_pro)
                for i in range(lenpro):
                    pp = self.all_models_pro[i]
                    if pp[0] < minnn1:
                        minnn2 = minnn1
                        id2 = id1
                        id1 = i
                    elif pp[0] < minnn2:
                        minnn2 = pp[0]
                        id2 = i
                # print('Yeeeeeeeeeeeeeeeeee')
                # return self.get_obs(), 0, False, '_'
                num1, num2 = id1, id2
            else:
                num1, num2 = from_j, to_i
            if num1 == num2:
                    num2 = self.find_another(num1)
            name_list = []
            print(f'num1 = {num1}, num2 = {num2}')
            # print(f'lenall = {len(self.all_models_pro)}, id1 = {len(self.all_models_pro[num1])},id2 = {len(self.all_models_pro[num2])}')
            for name in self.all_models_pro[num1][3]:
                name_list.append(name)
            for name in self.all_models_pro[num2][3]:
                name_list.append(name)

            previous_acc = (self.all_models_pro[num1][1] + self.all_models_pro[num2][1]) / 2
            self.acc_sum = self.acc_sum - self.all_models_pro[num1][1] * len(self.all_models_pro[num1][3]) - self.all_models_pro[num2][1] * len(self.all_models_pro[num2][3])

            tmpdel1 = copy.deepcopy(self.all_models_pro[num1])
            tmpdel2 = copy.deepcopy(self.all_models_pro[num2])
            # new_acc, _ = train_with_name_new_data.multiple_classes_model(name_list)
            new_acc = 90
            self.acc_sum = self.acc_sum + new_acc * len(name_list)
            # new_acc = self.cal_reward(self.all_models_pro[num1][4], self.all_models_pro[num2][4], self.all_models_pro[num1][1], self.all_models_pro[num2][1])
            new_add_list = [len(name_list), new_acc, copy.deepcopy(self.all_models_pro[num1][2]), copy.deepcopy(name_list)]

            # all_models_pro里面老的要删掉
            self.all_models_pro.remove(tmpdel1)
            self.all_models_pro.remove(tmpdel2)
            self.all_models_pro.append(copy.deepcopy(new_add_list))
            # return num1, num2
            return self.all_models_pro[num1][4], self.all_models_pro[num2][4]
            
            # if num1 == num_of_new_name or num2 == num_of_new_name:
            #     if num1 == num_of_new_name:
            #         return [num2], [name_list], num2, self.all_models_pro
            #     else:
            #         return [num1], [name_list], num1, self.all_models_pro
        else:
            return -1, -1
    
    
    def run_a_list_every_step(self, new_question_list, up_GPU):
        res_list = []
        up_num = int(min(28, (up_GPU * 1000) // 170))
        fini_num = 0
        for name in new_question_list:
            self.add_new_model(name)
            self.choose_action(up_num)
            fini_num = fini_num + 1
            self.avg_acc = self.acc_sum / fini_num
            res_list.append(self.avg_acc)
        return res_list
    def run_a_list_every_step_for_size(self, new_question_list, up_GPU):
        file_size_dict = {0: 0, 1: 0, 2: 170648461, 3: 170656653, 4: 170664845, 5: 170673037, 6: 170681229, 7: 170689421, 8: 170697613, 9: 170705805, 10: 170713997, 11: 170722189, 12: 170730381, 13: 170738573, 14: 170746765, 15: 170754957, 16: 170763149, 17: 170771405, 18: 170779597, 19: 170787789, 20: 170795981, 21: 170804173, 22: 170812365, 23: 170820557, 24: 170828749, 25: 170836941, 26: 170845133, 27: 170853325, 28: 170861517, 29: 170869709, 30: 170877901, 31: 170886093, 32: 170894285, 33: 170902541, 34: 170910733, 35: 170918925, 36: 170927117, 37: 170935309, 38: 170943501, 39: 170951693, 40: 170959885, 41: 170968077, 42: 170976269, 43: 170984461, 44: 170992653, 45: 171000845, 46: 171009037, 47: 171017229, 48: 171025421, 49: 171033677, 50: 171041869}
        res_list = []
        up_num = int(min(28, (up_GPU * 1000) // 170))
        for name in new_question_list:
            self.add_new_model(name)
            self.choose_action(up_num)
            sum_size = 0
            for pp in self.all_models_pro:
                sum_size = sum_size + file_size_dict[pp[0] + 1]
            res_list.append(sum_size)
        print(f'len pro = {len(self.all_models_pro)}')
        return res_list
    def get_all_name_list(self):
        res_list = []
        for ll in self.all_models_pro:
            res_list.append(ll[3])
        return res_list
    def run_a_list_every_step_for_example(self, new_question_list, up_GPU):
        up_num = int(min(28, (up_GPU * 1000) // 170))
        res_list = []
        for name in new_question_list:
            self.add_new_model(name)
            self.choose_action(up_num)
            res_list.append(self.get_all_name_list())
            
        return res_list
    def run_a_list(self, new_question_list, up_GPU):

        up_num = int(min(28, (up_GPU * 1000) // 170))
        fini_num = 0
        for name in new_question_list:
            self.add_new_model(name)
            self.choose_action(up_num)
            fini_num = fini_num + 1
            self.avg_acc = self.acc_sum / fini_num
        print(self.all_models_pro)
        return self.avg_acc
    
    def write_state_to_json(self, json_path):
        # len_all_pro = len(self.all_models_pro)
        write_dict = {0 : self.all_models_pro}
        with open(json_path,"w") as f:
            json.dump(write_dict,f)
        
            

if __name__ == '__main__':
    ddpg = DDPG_USE()
    
    word_list = ['people', 'cat', 'dog', 'child', 'bird']
    ddpg.run_a_list(word_list, 1)
    ddpg.write_state_to_json('/root/code/edge/model_record/usr1/models.json')

    
