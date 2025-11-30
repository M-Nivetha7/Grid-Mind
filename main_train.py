# main_train.py
import time
from core.traffic_env import TrafficEnv
from agent.dqn_agent import DQNAgent
from app.dashboard import print_episode_summary

def main():
    env = TrafficEnv(render=False)
    state_dim = 4  # [n_e, v_e, n_s, v_s]
    action_dim = 2

    agent = DQNAgent(state_dim, action_dim)
    num_episodes = 50
    target_update_freq = 5

    for ep in range(num_episodes):
        state = env.reset()
        done = False
        total_reward = 0.0

        for _ in range(1000):
            action = agent.select_action(state, explore=True)
            # fixed dt, e.g., 1/FPS seconds
            dt = 1.0 / 30.0
            next_state, reward, done, _ = env.step(action, dt)
            agent.store(state, action, reward, next_state, done)
            agent.update()
            state = next_state
            total_reward += reward
            if done:
                break

        agent.update_target()
        fuel, co2 = env.metrics.estimate_emissions()
        print_episode_summary(ep, total_reward, env.metrics.total_wait_time, fuel, co2)

    env.close()

if __name__ == "__main__":
    main()
