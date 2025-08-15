from adafruit_pca9685 import PCA9685

class PCA9685Controller:
    def __init__(self, i2c, address=0x40, freq=50, min_us=500, max_us=2200):
        self.pca = PCA9685(i2c, address=address)
        self.pca.frequency = freq
        self.min_us = min_us
        self.max_us = max_us

    def _angle_to_duty(self, angle):
        """Convert 0-180° angle to 16-bit duty."""
        pulse_length = 1_000_000 / self.pca.frequency  # μs per period
        duty = int(((angle / 180.0) * (self.max_us - self.min_us) + self.min_us) /
                   pulse_length * 0xFFFF)
        return max(0, min(0xFFFF, duty))

    def set_servo_angle(self, channel, angle):
        """Set a single servo channel to angle (0-180)."""
        angle = max(0.0, min(180.0, angle))
        duty = self._angle_to_duty(angle)
        self.pca.channels[channel].duty_cycle = duty

    def set_servo_angles(self, angles, channels=None):
        """
        Move multiple servos at once.

        :param angles: list/tuple of angles (0-180). If channels provided, will map angles[i] to channels[i].
        :param channels: optional list/tuple of PCA9685 channels to update.
        """
        if channels is None:
            # assume angles are in channel order starting at 0
            for channel, angle in enumerate(angles):
                self.set_servo_angle(channel, angle)
        else:
            if len(channels) != len(angles):
                raise ValueError("Length of channels and angles must match")
            for ch, angle in zip(channels, angles):
                self.set_servo_angle(ch, angle)

