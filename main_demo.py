# main_demo.py
import pygame
from core.traffic_env import TrafficEnv
from smart_controller import SmartController

def main():
    env = TrafficEnv(render=True)
    controller = SmartController(max_red_time=20.0)
    controller.reset()

    running = True
    clock = pygame.time.Clock()
    state = env.reset()

    while running:
        dt_ms = clock.tick(30)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get current state from env
        state = env.get_simple_state()

        # Decide which phase to use
        phase_action = controller.decide(state)

        # Step environment with that phase
        env.step(phase_action, dt)

        # Render
        env.render()

    env.close()

if __name__ == "__main__":
    main()
