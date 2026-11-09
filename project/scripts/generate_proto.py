"""Compile vendored, pinned upstream proto definitions without network access."""
from pathlib import Path
import subprocess
import sys
import grpc_tools

root = Path(__file__).resolve().parents[1]
include = Path(grpc_tools.__file__).parent / "_proto"
subprocess.run([sys.executable, "-m", "grpc_tools.protoc", f"-I{root / 'proto'}",
                f"-I{include}", f"--python_out={root}", f"--grpc_python_out={root}",
                str(root / "proto/kuksa/val/v2/types.proto"),
                str(root / "proto/kuksa/val/v2/val.proto")], check=True)
print("Generated kuksa.val.v2 Python bindings from pinned upstream files.")
