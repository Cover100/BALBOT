from adafruit_pca9685 import PCA9685

class PCA9685Controller:
    def __init__(self, i2c, address=0x40, freq=50, min_us=500, max_us=2200):
        self.pca = PCA9685(i2c, address=address)
        self.pca.frequency = freq
        self.min_us = min_us
        self.max_us = max_us

    def set_servo_angles(self, angles):
        """
        Move multiple servos at once.
        
        :param angles: list or tuple of angles (0-180°)
                       Index corresponds to PCA9685 channel.
        """
        pulse_length = 1_000_000 / self.pca.frequency  # μs per period

        for channel, angle in enumerate(angles):
            # Clamp angle to valid range
            angle = max(0, min(180, angle))
            # Convert angle to 16-bit duty cycle
            duty = int(((angle / 180) * (self.max_us - self.min_us) + self.min_us) /
                       pulse_length * 0xFFFF)
            self.pca.channels[channel].duty_cycle = duty
