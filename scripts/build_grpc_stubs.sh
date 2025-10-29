# gRPC stubs build helper
python -m grpc_tools.protoc \
  -I mangle/proto \
  --python_out=reasoning/generated \
  --grpc_python_out=reasoning/generated \
  mangle/proto/reasoning.proto
