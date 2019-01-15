import matplotlib.pyplot as plt
import torch
import numpy as np
import random
from torch.optim import Adam
from model.DQN import DQNUnit
from utils.config import Config

config = Config('./config')


class Agent:
    type = "prey"  # or predator
    id = 0
    # For RL
    gamma = 0.9
    epsilon_greedy = 0.01
    lr = 0.1
    update_frequency = 0.1
    update_type = "hard"

    def __init__(self, type, agent_id, device, agent_config):
        assert type in ["prey", "predator"], "Agent type is not correct."
        self.type = type
        self.id = agent_id
        self.memory = None
        self.number_actions = agent_config.number_actions

        # For RL
        self.gamma = agent_config.gamma
        self.epsilon_greedy = agent_config.epsilon_greedy
        self.lr = agent_config.lr
        self.update_frequency = agent_config.update_frequency
        assert agent_config.update_type in ["hard", "soft"], "Update type is not correct."
        self.update_type = agent_config.update_type

        self.colors = {"prey": "#a1beed", "predator": "#ffd2a0"}

        self.device = device

    def draw_action(self, observation):
        raise NotImplementedError

    def update(self, *params):
        if self.update_type == "hard":
            self.hard_update(*params)
        elif self.update_type == "soft":
            self.soft_update(*params)

    def plot(self, position, radius, ax: plt.Axes):
        x, y = position
        circle = plt.Circle((x, y), radius=radius, color=self.colors[self.type])
        ax.add_artist(circle)
        ax.text(x, y, self.id)

    def soft_update(self, *params):
        raise NotImplementedError

    def hard_update(self, *params):
        raise NotImplementedError

    def learn(self, batch):
        raise NotImplementedError

    def save(self, name):
        raise NotImplementedError

    def load(self, name):
        raise NotImplementedError


class AgentDQN(Agent):
    def __init__(self, type, agent_id, device, agent_config):
        super(AgentDQN, self).__init__(type, agent_id, device, agent_config)

        self.policy_net = DQNUnit().to(self.device)
        self.target_net = DQNUnit().to(self.device)
        self.policy_optimizer = Adam(self.policy_net.parameters(), lr=config.agents.lr)
        self.hard_update(self.target_net, self.policy_net)

    def hard_update(self, target, policy):
        """
        Copy network parameters from source to target
        """
        target.load_state_dict(policy.state_dict())

    def draw_action(self, observation):
        p = np.random.random()
        if p < self.epsilon_greedy:
            action_probs = self.policy_net(observation)
            action = np.argmax(action_probs[0])
        else:
            action = random.randrange(self.number_actions)
        return action

    def load(self, name):
        params = torch.load(name)
        self.policy_net.load_state_dict(params['policy'])
        self.target_net.load_state_dict(params['target_policy'])
        self.policy_optimizer.load_state_dict(params['policy_optimizer'])

    def save(self, name):
        save_dict = {'policy': self.policy_net.state_dict(),
                     'target_policy': self.target_net.state_dict(),
                     'policy_optimizer': self.policy_optimizer.state_dict()}
        torch.save(save_dict, name)

    def learn(self, batch):
        pass
