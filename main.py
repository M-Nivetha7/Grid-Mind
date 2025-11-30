import pygame
from core.traffic_env import TrafficEnv
from smart_controller import SmartController
from core.config import FPS

def main():
    env = TrafficEnv(render=True)
    controller = SmartController()
    controller.reset()
    env.reset()

    running = True
    clock = pygame.time.Clock()

    while running:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state = env.get_state()
        phase = controller.decide(state)
        env.step(phase, dt)
        env.render()

    env.close()

if __name__ == "__main__":
    main()
