import time

class ADS7830ADC:
    def __init__(self, i2c, address=0x4B, min_voltages=None, max_voltages=None):
        """
        :param i2c: shared I2C bus
        :param address: ADC I2C address
        :param min_voltages: list of voltages corresponding to 180° for each servo
        :param max_voltages: list of voltages corresponding to 0° for each servo
        """
        self.i2c = i2c
        self.address = address
        self.min_voltages = min_voltages
        self.max_voltages = max_voltages

    def read_channel(self, channel):
        """Read voltage from a single ADC channel (0–7). Single sample."""
        if not 0 <= channel <= 7:
            raise ValueError("Channel must be between 0–7")

        cmd = 0x84 | (channel << 4)
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.writeto(self.address, bytes([cmd]))
            result = bytearray(1)
            self.i2c.readfrom_into(self.address, result)
        finally:
            self.i2c.unlock()

        return result[0] * 3.3 / 255  # scale to voltage

    def read_channel_avg(self, channel, samples=5, delay=0.003):
        """Averaged read to reduce noise."""
        vals = []
        for _ in range(max(1, samples)):
            vals.append(self.read_channel(channel))
            if delay:
                time.sleep(delay)
        return sum(vals) / len(vals)

    def read_channels(self, channels, samples=1, delay=0.003):
        """Read multiple channels at once (averaged if samples>1)."""
        if isinstance(channels, int):
            return self.read_channel_avg(channels, samples, delay) if samples > 1 else self.read_channel(channels)
        elif isinstance(channels, (list, tuple)):
            return [self.read_channel_avg(ch, samples, delay) if samples > 1 else self.read_channel(ch) for ch in channels]
        else:
            raise TypeError("channels must be int, list, or tuple")

    def voltage_to_angle(self, channel, voltage):
        """
        Map a feedback voltage to an angle (0–180°) using stored min/max voltages.
        Handles inverted mapping automatically and includes guards.
        """
        if self.min_voltages is None or self.max_voltages is None:
            raise ValueError("Min and max voltages not set. Initialize first.")

        # basic bounds check
        if channel < 0 or channel >= len(self.min_voltages) or channel >= len(self.max_voltages):
            raise IndexError(f"Channel {channel} not calibrated (check min/max arrays)")

        v_min = self.min_voltages[channel]  # voltage at 180°
        v_max = self.max_voltages[channel]  # voltage at 0°

        # guard against bad calibration
        if abs(v_min - v_max) < 1e-6:
            raise ValueError(f"Calibration error for channel {channel}: v_min == v_max")

        # Linear mapping (handles inverted sensors automatically)
        angle = (voltage - v_max) / (v_min - v_max) * 180.0

        # clamp and return
        if angle != angle:  # check NaN just in case
            return 0.0
        return max(0.0, min(180.0, angle))

    def read_angle(self, channel, samples=5, delay=0.003):
        """Read the voltage (averaged) and convert it to angle using voltage_to_angle."""
        voltage = self.read_channel_avg(channel, samples=samples, delay=delay)
        return self.voltage_to_angle(channel, voltage)

