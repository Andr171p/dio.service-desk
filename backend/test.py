"""
{
    "result": "ANSWERED | NO ANSWER | FAILED | BUSY"
    "billSec": 123
    "disposition": "OUTBOUND",
    "recordLink": "https://example.com",
}
"""

from typing import Any


def filter_calls(calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [call for call in calls if int(call.get("billSec", 0)) > 0]
