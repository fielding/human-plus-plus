"""
Human++ Python Sample

Async batch processor with rate limiting and error handling.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import AsyncIterator, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass(frozen=True)
class RateLimitConfig:
    requests_per_second: float = 10.0
    burst_size: int = 20
    retry_after_seconds: float = 1.0


@dataclass
class ProcessingResult(Generic[T]):
    success: bool
    value: T | None = None
    error: str | None = None
    duration_ms: float = 0.0


# !! Rate limiter is not distributed - only works for single instance
class TokenBucketRateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.burst_size)
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self._lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()
            self.tokens = min(
                self.config.burst_size,
                self.tokens + elapsed * self.config.requests_per_second
            )
            self.last_update = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

    async def wait_for_token(self) -> None:
        while not await self.acquire():
            await asyncio.sleep(0.1)


@dataclass
class BatchProcessor(Generic[T, R]):
    process_fn: Callable[[T], R]
    rate_limiter: TokenBucketRateLimiter
    max_concurrent: int = 10
    timeout_seconds: float = 30.0
    _semaphore: asyncio.Semaphore = field(init=False)

    def __post_init__(self):
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

    async def process_item(self, item: T) -> ProcessingResult[R]:
        start = datetime.now()

        try:
            await self.rate_limiter.wait_for_token()

            async with self._semaphore:
                result = await asyncio.wait_for(
                    asyncio.to_thread(self.process_fn, item),
                    timeout=self.timeout_seconds
                )

                duration = (datetime.now() - start).total_seconds() * 1000
                return ProcessingResult(
                    success=True,
                    value=result,
                    duration_ms=duration
                )

        except asyncio.TimeoutError:
            duration = (datetime.now() - start).total_seconds() * 1000
            return ProcessingResult(
                success=False,
                error="Processing timeout",
                duration_ms=duration
            )
        except Exception as e:
            duration = (datetime.now() - start).total_seconds() * 1000
            logger.exception("Processing failed")
            return ProcessingResult(
                success=False,
                error=str(e),
                duration_ms=duration
            )

    # ?? Should we add backpressure when too many failures occur?
    async def process_batch(
        self,
        items: list[T]
    ) -> AsyncIterator[tuple[T, ProcessingResult[R]]]:
        tasks = [
            asyncio.create_task(self._process_with_item(item))
            for item in items
        ]

        for task in asyncio.as_completed(tasks):
            item, result = await task
            yield item, result

    async def _process_with_item(
        self,
        item: T
    ) -> tuple[T, ProcessingResult[R]]:
        result = await self.process_item(item)
        return item, result


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    return text.strip().lower()


def compute_hash(data: bytes) -> str:
    """Compute SHA-256 hash of data."""
    import hashlib
    return hashlib.sha256(data).hexdigest()


# >> Entry point validates environment before starting processor
async def main() -> None:
    import os

    api_key = os.environ.get('API_KEY')
    if not api_key:
        raise RuntimeError("API_KEY environment variable required")

    config = RateLimitConfig(
        requests_per_second=5.0,
        burst_size=10
    )

    rate_limiter = TokenBucketRateLimiter(config)

    processor: BatchProcessor[str, str] = BatchProcessor(
        process_fn=normalize_text,
        rate_limiter=rate_limiter,
        max_concurrent=5
    )

    items = ["Hello World", "  Test Input  ", "UPPERCASE TEXT"]

    async for item, result in processor.process_batch(items):
        if result.success:
            print(f"Processed '{item}' -> '{result.value}' ({result.duration_ms:.1f}ms)")
        else:
            print(f"Failed '{item}': {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
