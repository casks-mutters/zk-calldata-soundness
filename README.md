# zk-calldata-soundness

## Overview
`zk-calldata-soundness` measures how much of a block’s gas usage is attributable to calldata (transaction input data). This is a key driver of data-availability costs for zk-rollups (Aztec, Zama, etc.) and bridges. By scanning recent blocks, the tool estimates the calldata gas share and highlights peaks and troughs that may affect proof batching costs and posting strategies.

##Features
- Calculates zero/non-zero calldata bytes and estimated calldata gas per block (4/16 gas per byte model)
- Reports calldata gas as a percentage of total `gasUsed`
- Includes base fee (Gwei), tx count, and timestamps per block
- Progress output with percentage; JSON report for CI/dashboards
- Works on any EVM-compatible RPC; no ABI or contract list required

## Installation
1) Python 3.9+
2) Install dependency:
   pip install web3
3) (Optional) Set a default RPC:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY

## Usage
Analyze the last 10 blocks:
   python app.py

Skip the newest 5 blocks (e.g., to avoid reorg windows), still analyze 10:
   python app.py --from-latest 5 --count 10

Use a custom RPC and analyze 50 blocks:
   python app.py --rpc https://arb1.arbitrum.io/rpc --count 50

Emit JSON for automation:
   python app.py --count 25 --json > calldata_report.json

Increase timeout for slow RPCs:
   python app.py --count 20 --timeout 60

## Expected Output
- For each block: prints block number, tx count, gasUsed, estimated calldata gas, and the percentage of gasUsed that is calldata gas.
- Summary includes:
  • Blocks analyzed
  • Average calldata gas share (%)
  • Average calldata bytes per block
  • Peak and lowest block by calldata gas share
- JSON mode outputs the per-block metrics and summary for easy thresholding in CI.

## Example (truncated)
🔧 zk-calldata-soundness
🧭 Chain ID: 1
🔗 RPC: https://mainnet.infura.io/v3/…
🧱 Range: 19999991 → 20000000 (count=10, skip_latest=0)
🕒 Start: 2025-11-08T21:05:18Z
🔍 Block 19999991 (1/10, 10.0%)
   📦 tx=182, gasUsed=29876543, calldataGas≈8420000 (28.19%)
…
📊 Summary
   • Blocks analyzed: 10
   • Avg calldata gas share: 27.45%
   • Avg calldata bytes per block: 450321
   • Peak block #19999998: 31.92% calldata gas share
   • Lowest block #19999992: 22.11% calldata gas share

## Notes
- Data model: Calldata gas is estimated as 4 gas per zero byte and 16 gas per non-zero byte of the transaction input (classic EVM pricing). This does not include intrinsic/other gas components.
- Blobs (EIP-4844): Blob data gas is separate from calldata. This tool focuses on calldata only and is still useful on L2s without blobs or for legacy DA analysis.
- Reorg safety: Use `--from-latest` to avoid the freshest blocks if you want finalized data.
- Performance: Full transactions are fetched for each block to inspect `input`; high `--count` values will increase RPC load.
- CI guidance: This tool never fails on thresholds; instead, parse JSON and assert on `summary.avg_calldata_gas_pct` or peaks.
- ZK impact: High calldata share increases DA costs for posting batches/proofs. Monitoring helps tune batch sizes, compression, or posting cadence.
- Privacy: Read-only analysis; no transactions are sent.
