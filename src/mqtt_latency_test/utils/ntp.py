import asyncio
import socket
import struct
import time
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("uvicorn.error")


class NTPSync:
    """
    NTP time synchronization utility with caching to avoid frequent network calls.
    Syncs with time.nist.gov and caches the time offset for efficient timestamp generation.
    """

    def __init__(self, ntp_server: str = "time.nist.gov", cache_duration: int = 30):
        """
        Initialize NTP synchronizer.

        Args:
            ntp_server: NTP server hostname (default: time.nist.gov)
            cache_duration: Cache duration in seconds (default: 30 seconds)
        """
        self.ntp_server = ntp_server
        self.cache_duration = cache_duration
        self.time_offset: Optional[float] = None
        self.last_sync_time: Optional[float] = None
        self._sync_lock = asyncio.Lock()

    async def _get_ntp_time(self) -> float:
        """
        Get NTP time from the server.

        Returns:
            NTP timestamp as float

        Raises:
            Exception: If NTP sync fails
        """
        # NTP packet format
        ntp_packet = b"\x1b" + 47 * b"\0"

        try:
            # Create socket and set timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)  # 5 second timeout

            # Send NTP request
            sock.sendto(ntp_packet, (self.ntp_server, 123))

            # Receive response
            response, _ = sock.recvfrom(1024)
            sock.close()

            # Extract timestamp from NTP response (bytes 40-43 for seconds)
            ntp_timestamp = struct.unpack("!12I", response)[10]

            # Convert from NTP epoch (1900) to Unix epoch (1970)
            # NTP epoch starts at 1900-01-01, Unix epoch at 1970-01-01
            # Difference is 70 years = 2208988800 seconds
            unix_timestamp = ntp_timestamp - 2208988800

            return float(unix_timestamp)

        except Exception as e:
            raise Exception(
                f"Failed to sync with NTP server {self.ntp_server}: {str(e)}"
            )

    async def _sync_time_offset(self) -> None:
        """
        Synchronize with NTP server and calculate time offset.
        """
        try:
            # Get current local time
            local_time = time.time()

            # Get NTP time
            ntp_time = await self._get_ntp_time()

            # Calculate offset
            self.time_offset = ntp_time - local_time
            self.last_sync_time = local_time

            logger.debug(f"NTP sync successful. Offset: {self.time_offset:.3f}s")

        except Exception as e:
            logger.debug(f"NTP sync failed: {e}")
            # If sync fails, we'll use local time (offset = 0)
            if self.time_offset is None:
                self.time_offset = 0.0
                self.last_sync_time = time.time()

    async def get_ntp_timestamp(self) -> float:
        """
        Get current NTP-synchronized timestamp.
        Uses cached offset if within cache duration, otherwise syncs with NTP server.

        Returns:
            Current timestamp synchronized with NTP server
        """
        current_time = time.time()

        # Check if we need to sync (first time or cache expired)
        needs_sync = (
            self.time_offset is None
            or self.last_sync_time is None
            or (current_time - self.last_sync_time) > self.cache_duration
        )

        if needs_sync:
            async with self._sync_lock:
                # Double-check in case another coroutine already synced
                if (
                    self.time_offset is None
                    or self.last_sync_time is None
                    or (time.time() - self.last_sync_time) > self.cache_duration
                ):
                    await self._sync_time_offset()

        # Return current time adjusted by NTP offset
        return current_time + (self.time_offset or 0.0)

    async def get_ntp_datetime(self) -> datetime:
        """
        Get current NTP-synchronized datetime in UTC.

        Returns:
            Current UTC datetime synchronized with NTP server
        """
        timestamp = await self.get_ntp_timestamp()
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def get_cache_status(self) -> dict:
        """
        Get current cache status for debugging.

        Returns:
            Dictionary with cache status information
        """
        if self.last_sync_time is None or self.time_offset is None:
            return {"status": "not_synced", "offset": None, "age": None}

        age = time.time() - self.last_sync_time
        is_valid = age <= self.cache_duration

        return {
            "status": "valid" if is_valid else "expired",
            "offset": self.time_offset,
            "age_seconds": age,
            "cache_duration": self.cache_duration,
            "last_sync": datetime.fromtimestamp(
                self.last_sync_time, tz=timezone.utc
            ).isoformat(),
        }


# Global NTP synchronizer instance
# Cache for 30 seconds to balance accuracy and performance for 0.7s API calls
ntp_sync = NTPSync(cache_duration=30)


async def get_ntp_timestamp() -> float:
    """
    Convenience function to get NTP timestamp.

    Returns:
        Current NTP-synchronized timestamp
    """
    return await ntp_sync.get_ntp_timestamp()


async def get_ntp_datetime() -> datetime:
    """
    Convenience function to get NTP datetime.

    Returns:
        Current NTP-synchronized datetime
    """
    return await ntp_sync.get_ntp_datetime()
