# app/dashboard.py

def print_episode_summary(ep, total_reward, total_wait, fuel, co2):
    print(f"[EP {ep}] reward={total_reward:.2f} wait={total_wait:.1f} fuel={fuel:.1f} co2={co2:.1f}")
