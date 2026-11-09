import unittest
from sdv_lab.can_frame import FRAME, PAYLOAD, CAN_ID, decode_frame
from sdv_lab.policy import SPEED, SOC, TEMP


class FrameTests(unittest.TestCase):
    def test_private_wire_format_scaling_and_signed_temperature(self):
        frame = FRAME.pack(CAN_ID, 8, PAYLOAD.pack(6000, 7000, -150, 255, 1))
        counter, values = decode_frame(frame)
        self.assertEqual(counter, 255)
        self.assertAlmostEqual(values[SPEED], 60)
        self.assertAlmostEqual(values[SOC], 70)
        self.assertAlmostEqual(values[TEMP], -15)

    def test_foreign_rtr_and_invalid_frames(self):
        payload = PAYLOAD.pack(6000, 7000, 470, 1, 1)
        self.assertIsNone(decode_frame(FRAME.pack(0x123, 8, payload)))
        self.assertIsNone(decode_frame(FRAME.pack(CAN_ID | 0x40000000, 8, payload)))
        for bad in [b"short", FRAME.pack(CAN_ID, 7, payload),
                    FRAME.pack(CAN_ID, 8, PAYLOAD.pack(6000, 10001, 470, 1, 1)),
                    FRAME.pack(CAN_ID, 8, PAYLOAD.pack(6000, 7000, 470, 1, 0))]:
            with self.subTest(frame=bad), self.assertRaises(ValueError):
                decode_frame(bad)
