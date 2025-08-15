import time
import board
import busio
import math
from pca9685_controller import PCA9685Controller
from ads7830_adc import ADS7830ADC
from pid_controller import PID

# -----------------------------
# Setup shared I2C bus
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)

# Create PCA9685 controller
servo_ctrl = PCA9685Controller(i2c)

# Temporary ADC object for initialization only
adc_temp = ADS7830ADC(i2c)

# -----------------------------
# Initialize servo feedback (same as you had)
# -----------------------------
def initialize_servo_feedback(servo_ctrl, adc, servo_channels=[0,1,2], settle_time=2.0):
    num_servos = len(servo_channels)
    servo_ctrl.set_servo_angles([180]*num_servos, channels=servo_channels)
    time.sleep(settle_time)
    min_voltages = adc.read_channels(servo_channels, samples=5)

    servo_ctrl.set_servo_angles([0]*num_servos, channels=servo_channels)
    time.sleep(settle_time)
    max_voltages = adc.read_channels(servo_channels, samples=5)

    print("Minimum voltages (180°):", min_voltages)
    print("Maximum voltages (0°):", max_voltages)

    return min_voltages, max_voltages

min_voltages, max_voltages = initialize_servo_feedback(
    servo_ctrl, adc_temp, servo_channels=[0,1,2], settle_time=2.0
)

# -----------------------------
# Create ADC object with voltage mapping
# -----------------------------
adc = ADS7830ADC(i2c, min_voltages=min_voltages, max_voltages=max_voltages)

# -----------------------------
# Closed-loop parameters
# -----------------------------
servo_channels = [0, 1, 2]        # physical channels you use
num_servos = len(servo_channels)

# PID controllers (one per servo). Start conservative.
pids = [
    PID(kp=0.6, ki=0.0, kd=0.02, out_min=-30, out_max=30, integ_limit=50.0)
    for _ in range(num_servos)
]

# control loop settings
dt = 0.05                        # loop period (s) -> 20 Hz
adc_samples = 7                  # samples per feedback read (averaging)
settle_after_cmd = 0.03          # small wait after commanding before reading feedback
max_delta_per_loop = 8.0         # degrees max change to command per loop (rate limiting)
tolerance_deg = 1.5              # acceptable error (deg) before correction needed

# initial targets (will typically change each loop)
target_angles = [45.0, 45.0, 45.0]

# initialize commanded angles to targets (open-loop start)
commanded_angles = list(target_angles)
servo_ctrl.set_servo_angles(commanded_angles, channels=servo_channels)
time.sleep(0.1)

# -----------------------------
# Main closed-loop loop
# -----------------------------
try:
    last_time = time.monotonic()
    while True:
        loop_start = time.monotonic()
        dt_actual = loop_start - last_time
        last_time = loop_start

        # THIS IS WHERE CONTROL SYSTEM NEEDS TO UPDATE
        # Example dynamic target:
        # freq = 0.05  # Hz
        # target_angles[0] = 90 + 45 * math.sin(2 * math.pi * freq * loop_start)

        # Command current commanded_angles (they may be updated below)
        servo_ctrl.set_servo_angles(commanded_angles, channels=servo_channels)

        # small settle before reading feedback
        time.sleep(settle_after_cmd)

        # Read feedback angles (averaged)
        feedback_angles = [adc.read_angle(ch, samples=adc_samples) for ch in servo_channels]

        # PID corrections & compute new commanded angles
        new_commanded = []
        for i, ch in enumerate(servo_channels):
            target = target_angles[i]
            feedback = feedback_angles[i]
            error = target - feedback  # positive means we are below target

            # quick acceptance check
            if abs(error) <= tolerance_deg:
                correction = 0.0
            else:
                correction = pids[i].update(error, dt_actual)

            # corrected command = target + correction (correction is in degrees)
            corrected = target + correction

            # clamp 0..180
            corrected = max(0.0, min(180.0, corrected))

            # rate limit change from current commanded_angles[i]
            delta = corrected - commanded_angles[i]
            if delta > max_delta_per_loop:
                corrected = commanded_angles[i] + max_delta_per_loop
            elif delta < -max_delta_per_loop:
                corrected = commanded_angles[i] - max_delta_per_loop

            new_commanded.append(corrected)

        commanded_angles = new_commanded

        # debug print (rounded)
        print(f"Target: {[round(t,1) for t in target_angles]} | Feedback: {[round(f,1) for f in feedback_angles]} | Cmd: {[round(c,1) for c in commanded_angles]}")

        # wait until next loop (simple fixed-rate loop)
        elapsed = time.monotonic() - loop_start
        sleep_time = max(0.0, dt - elapsed)
        time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Returning all servos to 180°...")
    servo_ctrl.set_servo_angles([180] * num_servos, channels=servo_channels)
    time.sleep(1)
    print("Servos moved to 180°. Exiting program.")

