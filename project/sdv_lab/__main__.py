"""Run from project/: python -m sdv_lab --help."""
import argparse
import json
import sys
import time
from .policy import Policy, Sample, INPUTS, MODE


def emit(**fields):
    print(json.dumps({"ts": time.time(), **fields}, ensure_ascii=False), flush=True)


def values(scenario, tick):
    presets = {"normal": (60.0, 70.0, 30.0), "warn": (60.0, 70.0, 47.0),
               "critical": (60.0, 70.0, 57.0), "low-soc": (110.0, 10.0, 30.0)}
    if scenario == "cycle":
        scenario = ("normal", "warn", "critical", "normal")[(tick // 6) % 4]
    return dict(zip(INPUTS, presets[scenario]))


def offline():
    policy = Policy()
    now = 1000.0
    for scenario, age in [("normal", 0), ("warn", 0), ("critical", 0),
                          ("normal", 0), ("normal", 10)]:
        samples = {p: Sample(v, now-age) for p, v in values(scenario, 0).items()}
        decision = policy.evaluate(samples, now)
        emit(transport="in-process", scenario=scenario, age=age,
             mode=decision.mode, reason=decision.reason)


def run(args):
    if args.command == "offline":
        offline()
        return 0
    # Allows the introductory exercise to work without installing gRPC.
    import grpc
    from .transport import Broker
    with Broker(args.broker, args.timeout) as broker:
        if args.command == "inspect":
            info = broker.info()
            emit(server=info.name, version=info.version)
            for path, sample in broker.read(INPUTS + (MODE,)).items():
                emit(path=path, value=sample.value, source_timestamp=sample.timestamp)
            return 0
        if args.command == "watch":
            try:
                for updates in broker.watch(INPUTS + (MODE,), args.seconds):
                    for path, sample in updates.items():
                        emit(path=path, value=sample.value, source_timestamp=sample.timestamp)
            except grpc.RpcError as exc:
                if exc.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
                    raise
            return 0
        policy = Policy(max_age=args.max_age)
        tick = 0
        failures = 0
        while args.iterations == 0 or tick < args.iterations:
            try:
                if args.command == "provider":
                    timestamp = time.time() - args.age
                    data = values(args.scenario, tick)
                    for path, value in data.items():
                        broker.publish(path, value, timestamp)
                    emit(component="provider", scenario=args.scenario, values=data)
                else:
                    samples = broker.read(INPUTS)
                    decision = policy.evaluate(samples, time.time())
                    broker.publish(MODE, decision.mode)
                    emit(component="advisor", mode=decision.mode, reason=decision.reason)
                failures = 0
            except grpc.RpcError as exc:
                if exc.code() not in (grpc.StatusCode.UNAVAILABLE,
                                      grpc.StatusCode.DEADLINE_EXCEEDED):
                    raise  # Schema/auth failures need a human fix, not retries.
                failures += 1
                policy.previous = "UNKNOWN"
                emit(component=args.command, mode="UNKNOWN", broker_error=exc.code().name,
                     note="broker output may retain an old value; check output timestamp")
                if failures >= 5:
                    return 2
            tick += 1
            if args.iterations == 0 or tick < args.iterations:
                time.sleep(args.interval)
    return 0


def main():
    parser = argparse.ArgumentParser(description="SDV lab: KUKSA VAL v2, advisory only")
    parser.add_argument("command", choices=["offline", "provider", "advisor", "inspect", "watch"])
    parser.add_argument("--broker", default="127.0.0.1:55555")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--iterations", type=int, default=0, help="0 = continuous")
    parser.add_argument("--scenario", choices=["normal", "warn", "critical", "low-soc", "cycle"], default="cycle")
    parser.add_argument("--age", type=float, default=0, help="inject source data age in seconds")
    parser.add_argument("--max-age", type=float, default=3)
    parser.add_argument("--seconds", type=float, default=30, help="watch deadline")
    args = parser.parse_args()
    if args.interval <= 0 or args.timeout <= 0 or args.iterations < 0 or args.seconds <= 0:
        parser.error("interval/timeout/seconds must be positive; iterations >= 0")
    try:
        return run(args)
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
