# controller_reference.py
#
# Leader-only reference controller for the 2026 Autonomous Newbie Project.
# This file is NOT for recruits.
#
# Sign convention:
# lane_offset_m:
#   negative = vehicle is left of lane center
#   positive = vehicle is right of lane center
#
# heading_error_deg:
#   negative = vehicle heading points left of desired direction
#   positive = vehicle heading points right of desired direction
#
# Steering output semantics:
# "LEFT" means command the vehicle to steer / move left.
# "RIGHT" means command the vehicle to steer / move right.
# Therefore:
# - positive lane_offset_m means vehicle is right of center, so LEFT is corrective
# - positive heading_error_deg means vehicle points right of desired direction, so LEFT is corrective

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
    Returns:
        (steering, speed_action)

        steering:
            "LEFT", "RIGHT", "STRAIGHT"

        speed_action:
            "ACCELERATE", "SLOW", "STOP"
    """

    # Thresholds kept simple and readable for this project.
    DANGER_OBSTACLE_M = 1.0
    CAUTION_OBSTACLE_M = 2.0

    MILD_HEADING_DEG = 3.0
    LARGE_HEADING_DEG = 15.0

    MILD_OFFSET_M = 0.15
    LARGE_OFFSET_M = 0.40

    HIGH_SPEED_MPS = 3.0

    # 1. Emergency handling
    if e_stop:
        return "STRAIGHT", "STOP"

    # 2. Sensor validity / uncertainty handling
    if not sensor_valid:
        return "STRAIGHT", "STOP"

    # 3. Obstacle handling
    if obstacle_distance_m <= DANGER_OBSTACLE_M:
        if not left_clear and not right_clear:
            return "STRAIGHT", "STOP"

        if left_clear and not right_clear:
            return "LEFT", "SLOW"

        if right_clear and not left_clear:
            return "RIGHT", "SLOW"

        # If both sides appear available, choose a conservative avoidance action.
        if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
            return "LEFT", "SLOW"

        if heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
            return "RIGHT", "SLOW"

        return "LEFT", "SLOW"

    if obstacle_distance_m <= CAUTION_OBSTACLE_M:
        if not left_clear and not right_clear:
            return "STRAIGHT", "STOP"

        if left_clear and not right_clear:
            return "LEFT", "SLOW"

        if right_clear and not left_clear:
            return "RIGHT", "SLOW"

        # If both sides appear available, stay conservative.
        if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
            return "LEFT", "SLOW"

        if heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
            return "RIGHT", "SLOW"

        return "STRAIGHT", "SLOW"

    # 4. Heading correction
    # Large heading/lateral error at nontrivial speed should not be treated as harmless.
    if speed_mps >= HIGH_SPEED_MPS:
        if heading_error_deg > LARGE_HEADING_DEG or lane_offset_m > LARGE_OFFSET_M:
            return "LEFT", "SLOW"

        if heading_error_deg < -LARGE_HEADING_DEG or lane_offset_m < -LARGE_OFFSET_M:
            return "RIGHT", "SLOW"

    # Mild drift without immediate danger should only trigger a modest correction.
    if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
        return "LEFT", "ACCELERATE"

    if heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
        return "RIGHT", "ACCELERATE"

    # 5. Normal behaviour / conservative fallback
    return "STRAIGHT", "ACCELERATE"
