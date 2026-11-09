"""Real gRPC serialization over loopback, using a SMALL TEST FIXTURE.

This fixture is not KUKSA and does not prove compatibility with the broker.
The separate smoke_live.py checks that compatibility.
"""
from concurrent.futures import ThreadPoolExecutor
import unittest
import grpc
from kuksa.val.v2 import val_pb2 as val, val_pb2_grpc
from sdv_lab.transport import Broker, encode, decode
from sdv_lab.policy import INPUTS, MODE, Policy


class Fixture(val_pb2_grpc.VALServicer):
    def __init__(self):
        self.points = {}

    def PublishValue(self, request, context):
        self.points[request.signal_id.path] = request.data_point
        return val.PublishValueResponse()

    def GetValues(self, request, context):
        return val.GetValuesResponse(data_points=[self.points[x.path] for x in request.signal_ids])

    def Subscribe(self, request, context):
        yield val.SubscribeResponse(entries={p: self.points[p] for p in request.signal_paths})


class TransportTests(unittest.TestCase):
    def test_timestamp_and_missing_value(self):
        point = encode(30.0, 1234.125)
        self.assertEqual(decode(point).timestamp, 1234.125)
        from kuksa.val.v2.types_pb2 import Datapoint
        self.assertIsNone(decode(Datapoint()).value)
        self.assertIsNone(decode(Datapoint()).timestamp)

    def test_v2_wire_calls(self):
        fixture = Fixture()
        server = grpc.server(ThreadPoolExecutor(max_workers=2))
        val_pb2_grpc.add_VALServicer_to_server(fixture, server)
        port = server.add_insecure_port("127.0.0.1:0")
        self.assertGreater(port, 0)
        server.start()
        try:
            with Broker(f"127.0.0.1:{port}") as broker:
                for path, value in zip(INPUTS, (60, 70, 57)):
                    broker.publish(path, value, timestamp=1000)
                data = broker.read(INPUTS)
                self.assertEqual(Policy().evaluate(data, 1000).mode, "CRITICAL")
                broker.publish(MODE, "CRITICAL", 1000)
                self.assertEqual(broker.read((MODE,))[MODE].value, "CRITICAL")
                updates = broker.watch(INPUTS, seconds=2)
                try:
                    self.assertEqual(set(next(updates)), set(INPUTS))
                finally:
                    updates.close()
        finally:
            server.stop(0).wait()


if __name__ == "__main__":
    unittest.main()
