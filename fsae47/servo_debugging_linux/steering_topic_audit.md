# Steering Signal Audit (ROS 2 source-based)

This document captures concrete, code-backed candidates for steering-related signals.

## Primary control chain in autonomous launch

1. `fsae_control/stanley_controller.py` computes `self.steering_angle` and publishes `AckermannDriveStamped` on relative topic `cmd_vel`.
2. In `gocart_bringup/launch/gocart_autonomous.launch.py`, this node runs under namespace `moa`, so the runtime topic is `/moa/cmd_vel`.
3. `gocart_control/ack_to_can.py` subscribes to relative topic `cmd_vel`; under `moa` namespace this resolves to `/moa/cmd_vel`.
4. `ack_to_can` encodes steering angle into CAN byte payload and publishes `fsae_interfaces/CANStamped` on `pub_raw_can` (runtime `/moa/pub_raw_can`).

## Candidates found

### Commanded steering angle (Ackermann)

- `/moa/cmd_vel` (`ackermann_msgs/AckermannDriveStamped`) from `stanley_controller` in autonomous launch.
- `/cmd_vel` (`ackermann_msgs/AckermannDriveStamped`) in base/test/teleop launch contexts (no namespace).
- `/cmd_vel` (`ackermann_msgs/AckermannDriveStamped`) from `trajectory_follower` (if used instead of Stanley).
- `/cmd_val` (`ackermann_msgs/AckermannDriveStamped`) in scrutineering mission node (test path).

### Intermediate/transformed steering

- `/moa/drive` (`ackermann_msgs/AckermannDrive`) from Stanley controller (same steering angle in unstamped message).
- `/moa/drive_vis` (`ackermann_msgs/AckermannDrive`) from Stanley controller (visualisation duplicate).
- `/test/cmd_steering`-style (`std_msgs/Float32`) from trajectory follower simulation output only.
- `/moa/selected_steering_angle` (`std_msgs/Float32`) consumed by trajectory follower as an upstream steering target from planning.

### PWM / servo / actuator-level command

- `/moa/pub_raw_can` (`fsae_interfaces/CANStamped`) includes encoded steering command byte from `ack_msg.drive.steering_angle`.

### Measured steering angle (feedback candidate)

- `/drive_status` (`ackermann_msgs/AckermannStamped` as written in code) in `can_decoder_jnano.py` sets `drive_status_msg.drive.steering_angle` from raw CAN ID `0x605` byte `data[0]`.
- This node is **not launched** by current bringup files shown; measured steering appears available only if `gocart_driver/can_decoder_jnano` is separately launched and raw CAN feed (`/raw_can`) is connected.

## Important gaps

- No active publisher of `moa/curr_vel` was found in searched source; some nodes subscribe to it (`sys_status`, `inspection_mission`) expecting measured/current Ackermann state.
- If measured steering exists at runtime in your system, it may be produced by external nodes/packages, CanTalk integration, or hardware bridge not included in this tree.
