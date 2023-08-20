from collections import defaultdict
import os
from datetime import datetime
import pickle

import numpy as np

from rostok.graph_generators.environments.design_environment import STATESTYPE, DesignEnvironment

EPS = 1e-8


class MCTS:

    def __init__(self,
                 environment: DesignEnvironment,
                 c=1.4,
                 verbosity=0):

        self.c = c
        self.environment = environment
        self.verbosity = verbosity

        self.Qsa = defaultdict(float)  # total reward of each state-action pair
        self.Nsa = defaultdict(int)  # total visit count for each state-action pair
        self.Ns = defaultdict(int)  # total visit count for each state
        self.Vs = defaultdict(float)  # total reward of each state

    def get_policy(self, state: STATESTYPE):
        pi = np.zeros_like(self.environment.actions, dtype=np.float32)
        mask_actions = self.environment.get_available_actions(state)
        for a in self.environment.actions[mask_actions == 1]:
            pi[a] = 0.0 if self.Nsa[(state, a)] == 0 else self.Nsa[(state, a)]
        
        if np.sum(pi) == 0.0:
            pi = np.ones_like(self.environment.actions, dtype=np.float32)
            pi *= mask_actions
        pi /= np.sum(pi)
        return pi

    def search(self, state: STATESTYPE):

        if state not in self.Vs:
            is_terminal_s, __ = self.environment.is_terminal_state(state)
            self.Vs[state] = self.environment.terminal_states[state][0] if is_terminal_s else 0.0

        if self.Vs[state] != 0.0:
            return self.Vs[state]

        if state not in self.Ns:
            hat_V = self.default_policy(state)

            return hat_V

        best_action = self.tree_policy(state)

        new_state = self.environment.next_state(state, best_action)[0]

        v = self.search(new_state)

        self.update_Q_function(state, best_action, v)
        return v

    def update_Q_function(self, state, action, reward):

        if (state, action) in self.Qsa:
            self.Qsa[(
                state,
                action)] += (reward - self.Qsa[(state, action)]) / (self.Nsa[(state, action)])
            self.Nsa[(state, action)] += 1
        else:
            self.Qsa[(state, action)] = reward
            self.Nsa[(state, action)] = 1

        if state in self.Ns:
            self.Ns[state] += 1
        else:
            self.Ns[state] = 1

    def default_policy(self, state):
        rewards = []

        mask = self.environment.get_available_actions(state)
        available_actions = self.environment.actions[mask == 1]

        for a in available_actions:

            s, reward, is_terminal_state, __ = self.environment.next_state(state, a)
            while not is_terminal_state:
                mask = self.environment.get_available_actions(s)
                available_actions = self.environment.actions[mask == 1]
                rnd_action = np.random.choice(available_actions)

                s, reward, is_terminal_state, __ = self.environment.next_state(s, rnd_action)

            rewards.append(reward)
            self.update_Q_function(state, a, reward)

        return np.mean(rewards)

    def tree_policy(self, state):

        mask = self.environment.get_available_actions(state)
        available_actions = self.environment.actions[mask == 1]
        uct_score = self.uct_score(state)
        best_action = available_actions[np.argmax(uct_score)]

        return best_action
    
    def uct_score(self, state):
        mask = self.environment.get_available_actions(state)
        available_actions = self.environment.actions[mask == 1]
        
        state_action = [(state, a) for a in available_actions]
        Q = np.array([self.Qsa.get(sa, 0) for sa in state_action])
        N = np.array([self.Nsa.get(sa, 0) for sa in state_action])
        
        uct_scores = Q + self.c * np.sqrt(np.abs(np.log(self.Ns[state]) / (N + EPS)))
        
        return uct_scores
    
    def save(self, prefix, path = "./LearnedMCTS/"):
        os.path.split(path)
        if not os.path.exists(path):
            print(f"Path {path} does not exist. Creating...")
            os.mkdir(path)

        current_date = datetime.now()
        folder = f"{prefix}__{current_date.hour}h{current_date.minute}m_{current_date.second}s_date_{current_date.day}d{current_date.month}m{current_date.year}y"
        os_path = os.path.join(path, folder)
        print(f"Saving MCTS to {os_path}")
        os.mkdir(os_path)
        
        self.environment.save_environment(prefix="MCTS_env", path=os_path, use_date=False)
        
        file_names = [
            "Qsa.p", "Nsa.p", "Ns.p", "Vs.p"
        ]
        variables = [
            self.Qsa, self.Nsa, self.Ns, self.Vs
        ]
        for file, var in zip(file_names, variables):
            with open(os.path.join(os_path, file), "wb") as f:
                pickle.dump(var, f, protocol=pickle.HIGHEST_PROTOCOL)
                
    def load(self, path):
        
        self.environment.load_environment(os.path.join(path, "MCTS_env"))
        
        file_names = [
            "Qsa.p", "Nsa.p", "Ns.p", "Vs.p"
        ]
        variables = [
            self.Qsa, self.Nsa, self.Ns, self.Vs
        ]

        for file, var in zip(file_names, variables):
            with open(os.path.join(path, file), "rb") as f:
                var.update(pickle.load(f))

