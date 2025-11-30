# smart_controller.py

class SmartController:
    """
    Simple rule-based controller:
    - Chooses phase based on number of waiting cars.
    - Ensures no side stays red longer than max_red_time.
    Phases:
      0: NS green (south moves), EW red (east waits)
      1: EW green (east moves), NS red (south waits)
    """
    def __init__(self, max_red_time=20.0):
        self.max_red_time = max_red_time
        self.current_phase = 0

    def reset(self):
        self.current_phase = 0

    def decide(self, state):
        """
        state: dict from env.get_simple_state():
          - 'east_waiting'
          - 'south_waiting'
          - 'east_red_time'
          - 'south_red_time'
        Returns: phase (0 or 1)
        """
        east_wait = state["east_waiting"]
        south_wait = state["south_waiting"]
        east_red_t = state["east_red_time"]
        south_red_t = state["south_red_time"]

        # Fairness rule: if one side has been red too long and has waiting cars, give it green
        if east_wait > 0 and east_red_t >= self.max_red_time:
            self.current_phase = 1  # EW green
            return self.current_phase
        if south_wait > 0 and south_red_t >= self.max_red_time:
            self.current_phase = 0  # NS green
            return self.current_phase

        # Load-based choice: give green to side with more waiting cars
        if east_wait > south_wait:
            self.current_phase = 1  # EW green
        elif south_wait > east_wait:
            self.current_phase = 0  # NS green
        # if equal, keep current_phase

        return self.current_phase
