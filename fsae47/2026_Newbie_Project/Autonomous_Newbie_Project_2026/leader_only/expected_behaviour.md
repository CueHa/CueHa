# Expected Behaviour, Non-newbies Only

This document defines the intended high-level safe behaviour of the starter controller.

**newbies should NOT receive this document.**

## Core intended behaviour rules

- Rule 1, Emergency stop must dominate
- Rule 2, Unsafe uncertainty should not produce optimistic motion
- Rule 3, A dangerously close obstacle ahead with no safe side should result in stop
- Rule 4, Obstacle avoidance should take priority over lane-centering style behaviour
- Rule 5, If one side is safely available, the controller may steer toward the safe side
- Rule 6, Large heading error at nontrivial speed should not be treated as harmless
- Rule 7, Small drift without immediate danger should not trigger extreme action
- Rule 8, Higher-priority safety conditions must not be overwritten later by weaker logic
- Rule 9, Default behaviour should be conservative and sensible

## Expected high-level outcome by scenario

### 1. Clear Path, Centered
The vehicle should continue in a normal, stable way.
A reasonable outcome is to keep direction straight and allow forward motion without unnecessary correction.

### 2. Close Obstacle Ahead, No Safe Side
The vehicle should stop.
It should not continue forward, and it should not treat lane-centering or other minor conditions as more important than the immediate obstacle risk.

### 3. Obstacle Ahead, Left Clear
The vehicle should respond to the obstacle by steering left toward the available safe side.
Its speed behaviour should be conservative, typically slowing rather than accelerating aggressively.

### 4. Obstacle Ahead, Right Clear
The vehicle should respond to the obstacle by steering right toward the available safe side.
Its speed behaviour should be conservative, typically slowing rather than accelerating aggressively.

### 5. Large Heading Error at Speed
The vehicle should treat this as a meaningful control problem, not as a harmless state.
A reasonable outcome is to correct heading and avoid aggressive forward action until the heading error is reduced.

### 6. Emergency Stop Active
The vehicle should stop immediately.
No other condition, including obstacle logic, heading logic, or path availability, should override this outcome.

### 7. Obstacle Plus Heading Conflict
The vehicle should prioritize the safer obstacle response over weaker lower-priority correction behaviour.
It should not produce a contradictory or optimistic action, and it should behave conservatively in speed.

### 8. Mild Drift, No Obstacle
The vehicle should make a modest correction only.
It should not stop or behave as if the situation were safety-critical when there is no immediate obstacle and the deviation is small.