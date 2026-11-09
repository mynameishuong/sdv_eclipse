"""Pure advisory policy; no broker or hardware dependency.

Thresholds are teaching parameters, NOT battery manufacturer limits.
"""
from dataclasses import dataclass
import math

SPEED = "Vehicle.Speed"
SOC = "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current"
TEMP = "Vehicle.Lab.BatteryTemperature"
MODE = "Vehicle.Lab.AdvisoryMode"
INPUTS = (SPEED, SOC, TEMP)


@dataclass(frozen=True)
class Sample:
    value: object
    timestamp: float | None


@dataclass(frozen=True)
class Decision:
    mode: str
    reason: str


class Policy:
    def __init__(self, max_age: float = 3.0, max_skew: float = 0.5):
        if not math.isfinite(max_age) or max_age <= 0:
            raise ValueError("max_age must be finite and positive")
        self.max_age = max_age
        self.max_skew = max_skew
        self.previous = "UNKNOWN"

    def evaluate(self, samples: dict[str, Sample], now: float) -> Decision:
        for path in INPUTS:
            sample = samples.get(path)
            if sample is None or sample.timestamp is None:
                return self._result("UNKNOWN", f"missing value/timestamp: {path}")
            if (isinstance(sample.value, bool)
                    or not isinstance(sample.value, (int, float))
                    or not math.isfinite(sample.value)):
                return self._result("UNKNOWN", f"invalid numeric value: {path}")
            if not math.isfinite(sample.timestamp):
                return self._result("UNKNOWN", f"invalid timestamp: {path}")
            age = now - sample.timestamp
            if age > self.max_age:
                return self._result("UNKNOWN", f"stale: {path}")
            if age < -self.max_skew:
                return self._result("UNKNOWN", f"future timestamp: {path}")
        timestamps = [samples[p].timestamp for p in INPUTS]
        if max(timestamps) - min(timestamps) > self.max_skew:
            return self._result("UNKNOWN", "incoherent input timestamps")
        speed, soc, temp = (float(samples[p].value) for p in INPUTS)
        if not (0 <= speed <= 300 and 0 <= soc <= 100 and -40 <= temp <= 120):
            return self._result("UNKNOWN", "outside lab plausibility range")
        if temp >= 55 or (self.previous == "CRITICAL" and temp >= 52):
            return self._result("CRITICAL", "battery temperature high (lab threshold)")
        if temp >= 45 or (self.previous in ("WARN", "CRITICAL") and temp >= 42):
            return self._result("WARN", "battery temperature elevated (lab threshold)")
        if soc <= 15 and speed >= 100:
            return self._result("WARN", "low SOC while travelling fast (lab heuristic)")
        return self._result("NORMAL", "inputs fresh and within lab thresholds")

    def _result(self, mode: str, reason: str) -> Decision:
        # UNKNOWN clears hysteresis. A new valid sample is evaluated afresh.
        self.previous = mode
        return Decision(mode, reason)
