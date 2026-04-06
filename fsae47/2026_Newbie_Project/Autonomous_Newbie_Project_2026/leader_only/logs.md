1. Brief paragraph
   The 2026 Autonomous newbie project is a one-week, beginner-accessible, post-interview individual task in which every recruit receives the same simplified faulty autonomous vehicle controller. The controller will be paired with fixed scenarios and a simple visual playback tool. Recruits must diagnose the wrong behaviour, improve the controller, and present their reasoning, progress, results, and remaining limitations. Evaluation will prioritize reliability, debugging mindset, communication quality, engineering reasoning under ambiguity, and seriousness of engagement over perfect technical completion. 
2. What the project is meant to measure;
   1. Reliability and follow-through 
   2. Debugging mindset 
   3. Communication quality 
   4. Engineering reasoning under ambiguity 
   5. Initiative and workshop seriousness 
3. Controller inputs;
   1. obstacle_distance_m
   2. lane_offset_m
   3. heading_error_deg
   4. speed_mps
   5. e_stop
   6. left_clear
   7. right_clear
   8. sensor_valid
4. Controller outputs;
   1. steering: LEFT, RIGHT, STRAIGHT
   2. speed: ACCELERATE, SLOW, STOP
5. Locked planted fault categories
   1. Wrong priority ordering
      1. A lower-priority condition is allowed to dominate a higher-priority safety condition.
   2. Conflicting condition override
      1. One branch makes a sensible safety decision, but a later branch overwrites it with a weaker or contradictory action.
   3. Unsafe default behaviour
      1. If the state is unexpected, not well handled, or falls through the logic, the controller keeps moving or accelerates instead of taking a conservative action.
   4. Emergency stop not dominating
      1. The e-stop exists, but it is checked too late, applied inconsistently, or not enforced absolutely.

## Fault-to-scenario map

### Fault 1, Wrong priority ordering
Description:
A lower-priority condition is allowed to dominate a higher-priority safety condition.

Primary affected scenarios:
- Scenario 2, Close Obstacle Ahead, No Safe Side
- Scenario 3, Obstacle Ahead, Left Clear
- Scenario 4, Obstacle Ahead, Right Clear
- Scenario 7, Obstacle Plus Heading Conflict

What this fault would look like:
The controller may keep accelerating or keep treating itself as stable/centered even when obstacle response should already be taking priority.

---

### Fault 2, Conflicting condition override
Description:
One branch makes a sensible safety decision, but a later branch overwrites it with a weaker or contradictory action.

Primary affected scenarios:
- Scenario 3, Obstacle Ahead, Left Clear
- Scenario 4, Obstacle Ahead, Right Clear
- Scenario 5, Large Heading Error at Speed
- Scenario 7, Obstacle Plus Heading Conflict

What this fault would look like:
The controller may first slow down or choose an avoidance direction, then later replace that with accelerate or a contradictory steering output.

---

### Fault 3, Unsafe default behaviour
Description:
If the state is unexpected, poorly handled, or falls through the logic, the controller continues moving instead of choosing a conservative fallback.

Primary affected scenarios:
- Scenario 5, Large Heading Error at Speed
- Scenario 8, Mild Drift, No Obstacle

Secondary note:
This fault can also be exposed during any scenario if the recruit notices that unhandled combinations produce optimistic motion.

What this fault would look like:
The controller falls through to maintain speed or accelerate even when the state should have triggered caution.

---

### Fault 4, Emergency stop not dominating
Description:
The e-stop exists, but is checked too late, applied inconsistently, or not enforced absolutely.

Primary affected scenario:
- Scenario 6, Emergency Stop Active

Secondary affected scenario:
- Scenario 7, Obstacle Plus Heading Conflict

What this fault would look like:
The controller may still output steering or motion logic as though the e-stop were just another condition instead of an absolute stop command.

## For the visualizer;
It will be a simple 2D top-down fixed scenario playback tool at roughly turtlesim-level complexity, not a realistic simulator or game. It may use image assets for:

Background 
- Straight path with left path and right path open; 
- Straight path with left path open; 
- Straight path with right path open; 
- Straight path;

Sprite - Vehicle;
 - Vehicle_crash_front;
 - Vehicle_crash_left;
 - Vehicle_crash_right;
 - Obstacle_straight;
 - Obstacle_right;
 - Obstacle_left;

effects: a static failure overlay such as explosion

The vehicle will use short scripted movement playback for the 9 steering × speed combinations:

- straight / left / right
- stop / slow / accelerate

STOP should visually decelerate into no motion, SLOW should be conservative movement, and ACCELERATE should be more aggressive movement. Left/right acceleration may be shown as a larger curve, but it must not be treated as automatically bad by the visualizer itself. Failure indication should appear only when the outcome is clearly unsafe, such as colliding with an obstacle, entering a blocked side, or leaving the allowed area. The visualizer must remain fixed, lightweight, and easy to run, so recruits debug the controller, not the visualizer.