import unittest
from sdv_lab.policy import Policy, Sample, INPUTS, SPEED, SOC, TEMP


def samples(temp=30, soc=70, speed=60, stamp=1000):
    return {p: Sample(v, stamp) for p, v in zip(INPUTS, (speed, soc, temp))}


class PolicyTests(unittest.TestCase):
    def test_transitions_and_hysteresis(self):
        policy = Policy()
        for temp, expected in [(30, "NORMAL"), (45, "WARN"), (44, "WARN"),
                               (41, "NORMAL"), (55, "CRITICAL"), (53, "CRITICAL"),
                               (51, "WARN"), (41, "NORMAL")]:
            with self.subTest(temp=temp):
                self.assertEqual(policy.evaluate(samples(temp=temp), 1000).mode, expected)

    def test_missing_bad_values_and_bad_time(self):
        for path in INPUTS:
            for bad in (Sample(None, 1000), Sample(float("nan"), 1000),
                        Sample(float("inf"), 1000), Sample(True, 1000),
                        Sample(30, None), Sample(30, 900), Sample(30, 1001),
                        Sample(30, float("nan"))):
                with self.subTest(path=path, bad=bad):
                    data = samples()
                    data[path] = bad
                    self.assertEqual(Policy().evaluate(data, 1000).mode, "UNKNOWN")
            data = samples()
            del data[path]
            self.assertEqual(Policy().evaluate(data, 1000).mode, "UNKNOWN")

    def test_stale_even_if_get_succeeds(self):
        policy = Policy()
        data = samples()
        self.assertEqual(policy.evaluate(data, 1002).mode, "NORMAL")
        self.assertEqual(policy.evaluate(data, 1004).mode, "UNKNOWN")

    def test_low_soc_and_plausibility(self):
        self.assertEqual(Policy().evaluate(samples(speed=110, soc=10), 1000).mode, "WARN")
        for kwargs in ({"soc": 101}, {"temp": 121}, {"speed": -1}):
            self.assertEqual(Policy().evaluate(samples(**kwargs), 1000).mode, "UNKNOWN")

    def test_timestamp_coherence(self):
        data = samples()
        data[SPEED] = Sample(60, 999)
        self.assertEqual(Policy().evaluate(data, 1000).mode, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
