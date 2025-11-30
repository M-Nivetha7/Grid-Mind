# core/traffic_env.py
import pygame
import random

from .config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ROAD_WIDTH,
    CAR_LENGTH, CAR_WIDTH, CAR_SPEED, SPAWN_PROB_PER_FRAME,
    PHASE_MIN_DURATION_SEC, MAX_RED_TIME_SEC,
    COLOR_BLACK, COLOR_GRAY, COLOR_WHITE, COLOR_RED, COLOR_GREEN,
    COLOR_YELLOW, COLOR_BLUE,
    DIR_EAST, DIR_SOUTH,
    SAFETY_MARGIN,
)

# Size of the central conflict box (where roads cross)
CONFLICT_HALF_SIZE = ROAD_WIDTH // 2


class Car:
    def __init__(self, x, y, vx, vy, direction):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.direction = direction
        self.width = CAR_WIDTH
        self.length = CAR_LENGTH
        self.waiting = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.length)


class TrafficEnv:
    """
    1 intersection:
      - Phase 0: NS green (south moves), EW red (east waits)
      - Phase 1: EW green (east moves), NS red (south waits)
    You will pass in the phase from your controller.
    """
    def __init__(self, render=True):
        pygame.init()
        self.render_enabled = render
        if self.render_enabled:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Balanced Traffic Intersection")
        else:
            self.screen = None
        self.clock = pygame.time.Clock()

        self.cx = WINDOW_WIDTH // 2
        self.cy = WINDOW_HEIGHT // 2

        self.phase = 0
        self.phase_timer = 0.0

        self.cars = []
        self.time = 0.0

        # track red times
        self.red_time_east = 0.0
        self.red_time_south = 0.0

    def reset(self):
        self.cars = []
        self.phase = 0
        self.phase_timer = 0.0
        self.time = 0.0
        self.red_time_east = 0.0
        self.red_time_south = 0.0

    def spawn_cars(self):
        # Eastbound (from left → right)
        if random.random() < SPAWN_PROB_PER_FRAME:
            x = -CAR_LENGTH
            y = self.cy - ROAD_WIDTH // 4
            vx = CAR_SPEED
            vy = 0
            self.cars.append(Car(x, y, vx, vy, DIR_EAST))

        # Southbound (from top → down)
        if random.random() < SPAWN_PROB_PER_FRAME:
            x = self.cx - ROAD_WIDTH // 4
            y = -CAR_LENGTH
            vx = 0
            vy = CAR_SPEED
            self.cars.append(Car(x, y, vx, vy, DIR_SOUTH))

    def _ns_green(self):
        return self.phase == 0

    def _ew_green(self):
        return self.phase == 1

    def can_move(self, car):
        """
        Improved rule:
        - If a car is already inside the conflict box, always let it move (so it can leave).
        - If the box has ANY car inside, no new cars may ENTER it.
        - If the box is empty, cars from the green direction may enter,
          cars from the red direction must stop before it.
        """
        conflict_left   = self.cx - CONFLICT_HALF_SIZE
        conflict_right  = self.cx + CONFLICT_HALF_SIZE
        conflict_top    = self.cy - CONFLICT_HALF_SIZE
        conflict_bottom = self.cy + CONFLICT_HALF_SIZE

        conflict_rect = pygame.Rect(
            conflict_left,
            conflict_top,
            conflict_right - conflict_left,
            conflict_bottom - conflict_top,
        )

        rect = car.rect()

        # Is this car already inside the conflict box?
        in_conflict_now = rect.colliderect(conflict_rect)

        # 1) If car is in the box already, ALWAYS let it move so it can exit
        if in_conflict_now:
            return True

        # 2) Check if ANY other car is in the conflict box
        any_in_conflict = False
        for other in self.cars:
            if other is car:
                continue
            if other.rect().colliderect(conflict_rect):
                any_in_conflict = True
                break

        # If someone is already crossing, do not let new cars enter
        if any_in_conflict:
            # Outside cars cannot enter, but they may approach up to the box
            next_rect = rect.move(car.vx, car.vy)
            will_overlap = next_rect.colliderect(conflict_rect)
            if will_overlap:
                return False
            return True

        # 3) Box is empty → allow green side to enter, block red side
        next_rect = rect.move(car.vx, car.vy)
        will_overlap = next_rect.colliderect(conflict_rect)

        if will_overlap:
            if car.direction == DIR_EAST and self._ew_green():
                return True
            if car.direction == DIR_SOUTH and self._ns_green():
                return True
            return False

        # Far from the box and not entering this step → free to move
        return True

    def set_phase(self, phase):
        # 0 or 1
        self.phase = phase
        self.phase_timer = 0.0

    def step(self, phase_action, dt):
        """
        One step:
          - phase_action: 0 or 1 (chosen by controller)
          - dt: time step in seconds
        """
        # enforce min green
        self.phase_timer += dt
        if self.phase_timer >= PHASE_MIN_DURATION_SEC and phase_action != self.phase:
            self.set_phase(phase_action)

        # update red times
        if self._ew_green():
            # NS is red
            self.red_time_south += dt
            self.red_time_east = 0.0
        else:
            # EW is red
            self.red_time_east += dt
            self.red_time_south = 0.0

        self.spawn_cars()

        for car in self.cars:
            if self.can_move(car):
                car.waiting = False
                car.x += car.vx
                car.y += car.vy
            else:
                car.waiting = True

        # remove cars that left screen
        self.cars = [
            c for c in self.cars
            if -200 < c.x < WINDOW_WIDTH + 200 and -200 < c.y < WINDOW_HEIGHT + 200
        ]

        self.time += dt

    def get_state(self):
        """
        State for controller:
          - east_waiting: cars stopped on east approach
          - south_waiting: cars stopped on south approach
          - east_red_time
          - south_red_time
        """
        east_waiting = sum(1 for c in self.cars if c.direction == DIR_EAST and c.waiting)
        south_waiting = sum(1 for c in self.cars if c.direction == DIR_SOUTH and c.waiting)

        return {
            "east_waiting": east_waiting,
            "south_waiting": south_waiting,
            "east_red_time": self.red_time_east,
            "south_red_time": self.red_time_south,
        }

    def draw_roads(self):
        self.screen.fill(COLOR_BLACK)
        # horizontal
        pygame.draw.rect(
            self.screen,
            COLOR_GRAY,
            pygame.Rect(0, self.cy - ROAD_WIDTH // 2, WINDOW_WIDTH, ROAD_WIDTH)
        )
        # vertical
        pygame.draw.rect(
            self.screen,
            COLOR_GRAY,
            pygame.Rect(self.cx - ROAD_WIDTH // 2, 0, ROAD_WIDTH, WINDOW_HEIGHT)
        )

    def draw_cars(self):
        for car in self.cars:
            color = COLOR_BLUE if not car.waiting else COLOR_YELLOW
            pygame.draw.rect(self.screen, color, car.rect())

    def draw_signal(self):
        ns_color = COLOR_GREEN if self._ns_green() else COLOR_RED
        ew_color = COLOR_GREEN if self._ew_green() else COLOR_RED
        pygame.draw.circle(self.screen, ns_color, (self.cx - 60, self.cy - 60), 15)
        pygame.draw.circle(self.screen, ew_color, (self.cx + 60, self.cy + 60), 15)

    def render(self):
        if not self.render_enabled:
            return
        self.draw_roads()
        self.draw_cars()
        self.draw_signal()

        font = pygame.font.SysFont(None, 24)
        st = self.get_state()
        txt = font.render(
            f"Phase:{self.phase} EW_wait:{st['east_waiting']} NS_wait:{st['south_waiting']}",
            True,
            COLOR_WHITE,
        )
        self.screen.blit(txt, (10, 10))

        pygame.display.flip()

    def close(self):
        pygame.quit()
