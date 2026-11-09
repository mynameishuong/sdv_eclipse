"""Decode a PRIVATE teaching frame. This is not any OEM's CAN protocol."""
import struct
from .policy import SPEED, SOC, TEMP

CAN_ID = 0x321
FRAME = struct.Struct("=IB3x8s")  # Linux classical can_frame, 16 bytes
PAYLOAD = struct.Struct("<HHhBB")


def decode_frame(frame):
    if len(frame) != FRAME.size:
        raise ValueError("expected Linux classical CAN frame (16 bytes)")
    can_id, dlc, data = FRAME.unpack(frame)
    if can_id != CAN_ID:  # Also excludes RTR, EFF and ERR flag bits.
        return None
    if dlc != 8:
        raise ValueError("lab payload must have DLC=8")
    speed, soc, temp, counter, flags = PAYLOAD.unpack(data)
    if flags != 1:
        raise ValueError("lab frame is not marked valid")
    if speed > 30000 or soc > 10000 or not -400 <= temp <= 1200:
        raise ValueError("raw signal outside lab plausibility limits")
    return counter, {SPEED: speed * .01, SOC: soc * .01, TEMP: temp * .1}
