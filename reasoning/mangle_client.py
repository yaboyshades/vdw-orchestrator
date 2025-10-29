import asyncio
import grpc
import logging
from typing import Dict, Any

from core.models import ReasoningQuery, ReasoningResponse
from reasoning.generated import reasoning_pb2 as pb
from reasoning.generated import reasoning_pb2_grpc as pb_grpc

class MangleClient:
    def __init__(self, server_address: str = "localhost:50051"):
        self.server_address = server_address
        self.logger = logging.getLogger(self.__class__.__name__)
        self._channel: grpc.aio.Channel | None = None
        self._stub: pb_grpc.ReasoningServiceStub | None = None

    async def connect(self):
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(self.server_address)
            self._stub = pb_grpc.ReasoningServiceStub(self._channel)
            # Wait for channel ready
            await self._channel.channel_ready()
            self.logger.info(f"Connected to Mangle at {self.server_address}")

    async def disconnect(self):
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def query(self, reasoning_query: ReasoningQuery) -> ReasoningResponse:
        await self.connect()
        assert self._stub is not None
        req = pb.ReasoningRequest(
            query_id=reasoning_query.query_id,
            query_type=reasoning_query.query_type,
            facts=[],
            rules=[],
            goals=[],
        )
        try:
            resp: pb.ReasoningResponse = await self._stub.Query(req)
            return ReasoningResponse(
                query_id=resp.query_id,
                success=resp.success,
                result={},
                reasoning_trace=list(resp.reasoning_trace),
                confidence=resp.confidence,
                duration_ms=resp.duration_ms,
                allowed=getattr(resp, "allowed", None),
                reason=getattr(resp, "reason", None),
                missing_capabilities=list(getattr(resp, "missing_capabilities", [])),
                recommendations=list(getattr(resp, "recommendations", [])),
            )
        except grpc.aio.AioRpcError as e:
            self.logger.error(f"Mangle RPC error: {e}")
            return ReasoningResponse(
                query_id=reasoning_query.query_id,
                success=False,
                result={"error": str(e)},
                reasoning_trace=["grpc_error"],
                confidence=0.0,
                duration_ms=0.0,
                allowed=False,
                reason=str(e),
            )
