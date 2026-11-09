"""Thin adapter for the pinned upstream kuksa.val.v2 contract."""
from contextlib import AbstractContextManager
from datetime import datetime, timezone
import grpc
from kuksa.val.v2 import types_pb2 as types
from kuksa.val.v2 import val_pb2 as val
from kuksa.val.v2 import val_pb2_grpc
from .policy import Sample


def encode(value: object, timestamp: float | None = None) -> types.Datapoint:
    if isinstance(value, str):
        typed = types.Value(string=value)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        typed = types.Value(float=float(value))
    else:
        raise ValueError("lab supports only float and string signals")
    point = types.Datapoint(value=typed)
    moment = (datetime.now(timezone.utc) if timestamp is None
              else datetime.fromtimestamp(timestamp, timezone.utc))
    point.timestamp.FromDatetime(moment)
    return point


def decode(point: types.Datapoint) -> Sample:
    field = point.value.WhichOneof("typed_value") if point.HasField("value") else None
    value = getattr(point.value, field) if field else None
    stamp = (point.timestamp.seconds + point.timestamp.nanos / 1e9
             if point.HasField("timestamp") else None)
    return Sample(value, stamp)


class Broker(AbstractContextManager):
    def __init__(self, address: str, timeout: float = 2.0):
        # Plaintext is explicitly limited to the isolated learning network.
        self.channel = grpc.insecure_channel(address)
        self.stub = val_pb2_grpc.VALStub(self.channel)
        self.timeout = timeout

    def __exit__(self, *args):
        self.channel.close()

    def info(self):
        return self.stub.GetServerInfo(val.GetServerInfoRequest(), timeout=self.timeout)

    def read(self, paths):
        response = self.stub.GetValues(val.GetValuesRequest(
            signal_ids=[types.SignalID(path=p) for p in paths]), timeout=self.timeout)
        if len(response.data_points) != len(paths):
            raise ValueError("incomplete GetValues response")
        return {p: decode(dp) for p, dp in zip(paths, response.data_points)}

    def publish(self, path, value, timestamp=None):
        self.stub.PublishValue(val.PublishValueRequest(
            signal_id=types.SignalID(path=path), data_point=encode(value, timestamp)),
            timeout=self.timeout)

    def watch(self, paths, seconds=30):
        stream = self.stub.Subscribe(val.SubscribeRequest(
            signal_paths=list(paths), buffer_size=10), timeout=seconds)
        try:
            for response in stream:
                yield {path: decode(dp) for path, dp in response.entries.items()}
        finally:
            stream.cancel()
