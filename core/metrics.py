# core/metrics.py
import math

class MetricsTracker:
    """
    Tracks:
    - total_wait_time: accumulated time cars are stopped
    - total_cars: number of cars that have passed through
    - estimated_fuel, co2: simple estimates based on idle vs moving time
    """
    def __init__(self):
        self.total_wait_time = 0.0
        self.total_cars_passed = 0
        self.total_idle_time = 0.0
        self.total_moving_time = 0.0

    def reset(self):
        self.total_wait_time = 0.0
        self.total_cars_passed = 0
        self.total_idle_time = 0.0
        self.total_moving_time = 0.0

    def update_car_state(self, waiting, dt):
        if waiting:
            self.total_wait_time += dt
            self.total_idle_time += dt
        else:
            self.total_moving_time += dt

    def increment_cars_passed(self):
        self.total_cars_passed += 1

    def estimate_emissions(self):
        """
        Simple model:
        - idle_factor: fuel per second when waiting
        - move_factor: fuel per second when moving
        """
        idle_factor = 1.0
        move_factor = 0.5
        fuel_used = idle_factor * self.total_idle_time + move_factor * self.total_moving_time
        co2_factor = 2.3  # kg CO2 per unit of fuel (fake scale)
        co2 = fuel_used * co2_factor
        return fuel_used, co2
