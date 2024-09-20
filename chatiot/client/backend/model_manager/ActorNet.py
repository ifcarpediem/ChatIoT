import torch
import torch.nn as nn
import torch.nn.functional as F
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