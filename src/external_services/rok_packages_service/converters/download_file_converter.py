from collections.abc import AsyncIterator, AsyncGenerator
from typing import Any

from rok_bannerlord_proto.proto_vendor.rok_bannerlord_packages import DownloadFileQueryResponse


class DownloadFileConverter:
    @staticmethod
    async def to_internal(grpc_response: AsyncIterator[DownloadFileQueryResponse]) -> AsyncGenerator[bytes, Any]:
        async for response_chunk in grpc_response:
            yield response_chunk.content_chunk
