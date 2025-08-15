import time
import board
import busio
from pca9685_controller import PCA9685Controller
from ads7830_adc import ADS7830ADC

# -----------------------------
# Setup shared I2C bus
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)

# Create PCA9685 controller
servo_ctrl = PCA9685Controller(i2c)

# Temporary ADC object for initialization only
adc_temp = ADS7830ADC(i2c)

# -----------------------------
# Initialize servo feedback
# -----------------------------
def initialize_servo_feedback(servo_ctrl, adc, servo_channels=[0,1,2], settle_time=2.0):
    """
    Initializes servo feedback voltage range for mapping.
    Returns min_voltages (180°) and max_voltages (0°) for each servo.
    """
    num_servos = len(servo_channels)
    
    # Step 1: Move all servos to 180° and record min voltages
    servo_ctrl.set_servo_angles([180]*num_servos)
    time.sleep(settle_time)
    min_voltages = adc.read_channels(servo_channels)
    
    # Step 2: Move all servos to 0° and record max voltages
    servo_ctrl.set_servo_angles([0]*num_servos)
    time.sleep(settle_time)
    max_voltages = adc.read_channels(servo_channels)
    
    print("Minimum voltages (180°):", min_voltages)
    print("Maximum voltages (0°):", max_voltages)
    
    return min_voltages, max_voltages

# Initialize min/max voltages for ADC
min_voltages, max_voltages = initialize_servo_feedback(
    servo_ctrl, adc_temp, servo_channels=[0,1,2], settle_time=2.0
)

# -----------------------------
# Create ADC object with voltage mapping
# -----------------------------
adc = ADS7830ADC(i2c, min_voltages=min_voltages, max_voltages=max_voltages)

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        # Target angles for 3 servos
        servo_angles = [90, 180, 0]
        servo_ctrl.set_servo_angles(servo_angles)
        
        # Read mapped feedback angles from ADC
        feedback_angles = [adc.read_angle(ch) for ch in [0,1,2]]
        print(f"Target angles: {servo_angles} | Feedback angles: {[round(a,1) for a in feedback_angles]}")

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Returning all servos to 180°...")
    num_servos = 3
    servo_ctrl.set_servo_angles([180] * num_servos)
    time.sleep(1)
    print("Servos moved to 180°. Exiting program.")
