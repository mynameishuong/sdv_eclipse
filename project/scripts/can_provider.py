"""Linux only. Usage from project/: python -m scripts.can_provider --interface vcan0"""
import argparse
import socket
import time
from sdv_lab.can_frame import FRAME, decode_frame
from sdv_lab.transport import Broker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="vcan0")
    parser.add_argument("--broker", default="127.0.0.1:55555")
    args = parser.parse_args()
    if not hasattr(socket, "AF_CAN"):
        parser.error("SocketCAN requires a Linux Python interpreter")
    sock = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind((args.interface,))
    last = None
    # Broker loss terminates this adapter; supervisor must handle restarts.
    with sock, Broker(args.broker) as broker:
        while True:
            frame = sock.recv(FRAME.size)
            received_at = time.time()  # Gateway receive time, NOT ECU measurement time.
            try:
                decoded = decode_frame(frame)
                if decoded is None:
                    continue
                counter, values = decoded
                if counter == last:
                    print("Duplicate counter: sample dropped", flush=True)
                    continue
                if last is not None and counter != (last+1) % 256:
                    print(f"Counter gap/reset: {last} -> {counter}", flush=True)
                for path, value in values.items():
                    broker.publish(path, value, received_at)
                last = counter
            except ValueError as exc:
                print(f"CAN sample rejected: {exc}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
