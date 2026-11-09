"""Generate the private lab frame on vcan0. Never use on a vehicle bus."""
import argparse
import socket
import time
from sdv_lab.can_frame import CAN_ID, FRAME, PAYLOAD


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="vcan0")
    parser.add_argument("--temperature", type=float, default=47)
    parser.add_argument("--count", type=int, default=30)
    args = parser.parse_args()
    if args.interface != "vcan0":
        parser.error("sender is intentionally limited to the lab interface vcan0")
    if not -40 <= args.temperature <= 120 or args.count < 1:
        parser.error("temperature must be in [-40,120] and count >= 1")
    if not hasattr(socket, "AF_CAN"):
        parser.error("SocketCAN requires Linux")
    with socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW) as sock:
        sock.bind((args.interface,))
        for counter in range(args.count):
            payload = PAYLOAD.pack(6000, 7000, round(args.temperature*10), counter % 256, 1)
            sock.send(FRAME.pack(CAN_ID, 8, payload))
            time.sleep(1)


if __name__ == "__main__":
    main()
