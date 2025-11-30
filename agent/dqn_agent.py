# agent/dqn_agent.py
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(
        self,
        state_dim,
        action_dim,
        lr=1e-3,
        gamma=0.99,
        eps_start=1.0,
        eps_end=0.05,
        eps_decay=10000,
        buffer_size=50000,
        batch_size=64,
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.steps_done = 0

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_net = QNetwork(state_dim, action_dim).to(self.device)
        self.target_net = QNetwork(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)

        self.memory = []
        self.buffer_size = buffer_size

    def select_action(self, state, explore=True):
        eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * \
                        np.exp(-1.0 * self.steps_done / self.eps_decay)
        self.steps_done += 1

        if explore and random.random() < eps_threshold:
            return random.randrange(self.action_dim)

        with torch.no_grad():
            s = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            q_vals = self.q_net(s)
            return int(q_vals.argmax(dim=1).item())

    def store(self, s, a, r, ns, done):
        if len(self.memory) >= self.buffer_size:
            self.memory.pop(0)
        self.memory.append((s, a, r, ns, done))

    def update(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states_t = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(actions, dtype=torch.int64, device=self.device).unsqueeze(1)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states_t = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.float32, device=self.device).unsqueeze(1)

        q_values = self.q_net(states_t).gather(1, actions_t)

        with torch.no_grad():
            next_q = self.target_net(next_states_t).max(1)[0].unsqueeze(1)
            target = rewards_t + self.gamma * next_q * (1 - dones_t)

        loss = nn.functional.mse_loss(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target(self):
        self.target_net.load_state_dict(self.q_net.state_dict())
