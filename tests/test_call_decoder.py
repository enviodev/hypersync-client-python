"""Offline tests for the Python CallDecoder wrapper (no network needed)."""

import asyncio

import pytest

import hypersync

# transfer(0x000000000000000000000000000000000000dEaD, 1000)
_TRANSFER_INPUT = (
    "0xa9059cbb"
    "000000000000000000000000000000000000000000000000000000000000dead"
    "00000000000000000000000000000000000000000000000000000000000003e8"
)
_UNKNOWN_INPUT = "0xdeadbeef"


def _decoder() -> hypersync.CallDecoder:
    return hypersync.CallDecoder(["transfer(address to, uint256 amount)"])


def _assert_shape(out):
    assert len(out) == 2
    assert out[0] is not None and len(out[0]) == 2
    # Unmatched selectors decode to None.
    assert out[1] is None


def test_decode_inputs_sync():
    _assert_shape(_decoder().decode_inputs_sync([_TRANSFER_INPUT, _UNKNOWN_INPUT]))


def test_decode_inputs_async():
    _assert_shape(asyncio.run(_decoder().decode_inputs([_TRANSFER_INPUT, _UNKNOWN_INPUT])))


@pytest.mark.xfail(
    strict=True,
    reason="hypersync-client's CallDecoder::decode_input doesn't strip the 4-byte selector; "
    "remove once the Rust fix is released and bumped here",
)
def test_decode_inputs_values():
    to, amount = _decoder().decode_inputs_sync([_TRANSFER_INPUT])[0]
    assert to.val.lower() == "0x000000000000000000000000000000000000dead"
    assert amount.val == 1000
