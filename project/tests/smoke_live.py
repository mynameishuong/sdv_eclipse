"""Contract smoke against a REAL broker. Never starts a substitute broker.

Run with provider/advisor STOPPED. This script writes lab signals.
"""
import argparse
import time
import grpc
from sdv_lab.policy import Policy, INPUTS, MODE
from sdv_lab.transport import Broker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", default="127.0.0.1:55555")
    args = parser.parse_args()
    with Broker(args.broker) as broker:
        info = broker.info()
        print(f"Real broker: {info.name} {info.version}")
        assert info.version == "0.7.1", f"Expected pinned broker 0.7.1, got {info.version!r}"
        policy = Policy()
        for temp, expected in [(30, "NORMAL"), (47, "WARN"), (57, "CRITICAL"), (30, "NORMAL")]:
            stamp = time.time()
            for path, value in zip(INPUTS, (60.0, 70.0, float(temp))):
                broker.publish(path, value, stamp)
            data = broker.read(INPUTS)
            # Critical: prove broker preserves SOURCE timestamp, not GET time.
            for sample in data.values():
                assert sample.timestamp is not None and abs(sample.timestamp-stamp) < .001
            decision = policy.evaluate(data, time.time())
            assert decision.mode == expected, (decision, expected)
            broker.publish(MODE, decision.mode)
            assert broker.read((MODE,))[MODE].value == expected
            print(f"PASS temp={temp} -> {expected}")
        stamp = time.time()-10
        for path, value in zip(INPUTS, (60.0, 70.0, 30.0)):
            broker.publish(path, value, stamp)
        assert policy.evaluate(broker.read(INPUTS), time.time()).mode == "UNKNOWN"
        print("PASS stale source data -> UNKNOWN")
        for path, value, expected_code in [
            ("Vehicle.DoesNotExist", 1.0, grpc.StatusCode.NOT_FOUND),
            (INPUTS[0], "wrong-type", grpc.StatusCode.INVALID_ARGUMENT),
            (INPUTS[1], 101.0, grpc.StatusCode.INVALID_ARGUMENT),
        ]:
            try:
                broker.publish(path, value)
            except grpc.RpcError as exc:
                assert exc.code() == expected_code, exc
            else:
                raise AssertionError(f"Expected {expected_code.name} for {path}")
            print(f"PASS {path} rejects input with {expected_code.name}")
        # A subscription must return its initial snapshot.
        updates = broker.watch((INPUTS[0],), seconds=5)
        try:
            assert INPUTS[0] in next(updates)
        finally:
            updates.close()
        print("PASS v2 subscription initial snapshot")
    print("LIVE SMOKE PASSED")


if __name__ == "__main__":
    main()
