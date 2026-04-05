# controller.py
# Faulty decision logic for the 2026 Autonomous Newbie Project.
# Recruits will mainly modify this file.

VALID_STEERING = {"LEFT", "RIGHT", "STRAIGHT"}
VALID_SPEED = {"ACCELERATE", "SLOW", "STOP"}


def controller(
    obstacle_distance_m,
    lane_offset_m,
    heading_error_deg,
    speed_mps,
    e_stop,
    left_clear,
    right_clear,
    sensor_valid
):
    """
    Inputs:
        obstacle_distance_m: float
        lane_offset_m: float
        heading_error_deg: float
        speed_mps: float
        e_stop: bool
        left_clear: bool
        right_clear: bool
        sensor_valid: bool

    Returns:
        (steering, speed_action)

        steering must be one of:
            "LEFT", "RIGHT", "STRAIGHT"

        speed_action must be one of:
            "ACCELERATE", "SLOW", "STOP"
    """

    steering = "STRAIGHT"
    speed_action = "SLOW"

    # 1. Emergency handling
    # Highest-priority safety logic should be checked here.
    # If emergency stop is active, normal motion logic should not continue.

    # 2. Sensor validity handling
    # If sensing is invalid or unreliable, the controller should avoid optimistic behaviour.
    # Safe fallback behaviour should be considered here.

    # 3. Obstacle handling
    # Obstacle response should be decided here before lower-priority path-stability behaviour.
    # This includes deciding whether to stop, slow down, or steer toward a safe side.

    # 4. Heading correction
    # If there is no higher-priority safety issue, heading error can be used to choose a steering correction.
    # Large heading error at speed should not be ignored.

    # 5. Default cruise / normal behaviour
    # If no special condition applies, the controller should behave in a normal stable way.

    return steering, speed_action
