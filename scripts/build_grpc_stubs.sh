#!/usr/bin/env bash
set -euo pipefail

mkdir -p reasoning/generated
python -m grpc_tools.protoc \
  -I mangle/proto \
  --python_out=reasoning/generated \
  --grpc_python_out=reasoning/generated \
  mangle/proto/reasoning.proto

echo "gRPC stubs generated in reasoning/generated"