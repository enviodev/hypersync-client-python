import os
import asyncio
import hypersync
from dotenv import load_dotenv
from hypersync import TraceField

load_dotenv()

ADDR = "1e037f97d730Cc881e77F01E409D828b0bb14de0"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
BALANCE_OF_SIGHASH = "0x70a08231"
SIG_IN = "balanceOf(address)"
SIG_OUT = "balanceOf(address)(uint256)"


def make_client():
    token = os.getenv("ENVIO_API_TOKEN")
    if not token:
        raise ValueError("ENVIO_API_TOKEN is required")
    return hypersync.HypersyncClient(
        hypersync.ClientConfig(
            url="https://eth.hypersync.xyz",
            api_token=token,
        )
    )


async def main():
    client = make_client()
    height = await client.get_height()

    # recent window; increase if you get no traces
    from_block = max(0, height - 500_000)

    query = hypersync.Query(
        from_block=from_block,
        to_block=height,
        traces=[
            hypersync.TraceSelection(
                to=[USDC],
                sighash=[BALANCE_OF_SIGHASH],
            )
        ],
        field_selection=hypersync.FieldSelection(
            trace=[
                TraceField.INPUT,
                TraceField.OUTPUT,
                TraceField.TO,
                TraceField.SIGHASH,
                TraceField.CALL_TYPE,
                TraceField.TRANSACTION_HASH,
            ]
        ),
        max_num_traces=50,
    )

    res = await client.get(query)
    traces = [t for t in res.data.traces if t.input and t.output]

    print(f"got traces={len(res.data.traces)} usable={len(traces)}")
    if not traces:
        print("No usable traces with both input+output. Increase from_block window.")
        return

    decoder = hypersync.CallDecoder([SIG_IN])

    # 1) decode input (should contain the address argument)
    decoded_inputs = decoder.decode_traces_input_sync(traces)

    # filter to traces where the decoded address equals your ADDR
    target = "0x" + ADDR.lower()
    filtered_traces = []
    for tr, din in zip(traces, decoded_inputs):
        if not din:
            continue
        # din[0].val should be the address argument
        if isinstance(din[0].val, str) and din[0].val.lower() == target:
            filtered_traces.append(tr)

    print(f"traces calling balanceOf({target}) = {len(filtered_traces)}")
    if not filtered_traces:
        print("No traces found for that specific holder address in this window.")
        print("Still: decode_traces_output_sync can be tested without this filter.")
        filtered_traces = traces[:5]

    # 2) decode output (uint256 balance)
    sigs = [SIG_OUT] * len(filtered_traces)
    decoded_outputs = decoder.decode_traces_output_sync(filtered_traces, sigs)

    for i, (tr, dout) in enumerate(zip(filtered_traces[:5], decoded_outputs[:5])):
        print(f"\n[{i}] tx={tr.transaction_hash} call_type={tr.call_type} to={tr.to} sighash={tr.sighash}")
        print(f"  output={tr.output}")
        if dout is None:
            print("  decoded_output=None (missing output or signature mismatch)")
        else:
            print(f"  decoded_output_uint256={dout[0].val}")


if __name__ == "__main__":
    asyncio.run(main())
