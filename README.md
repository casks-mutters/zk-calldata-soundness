# zk-calldata-soundness

Overview
`zk-calldata-soundness` measures how much of a block’s gas usage is attributable to calldata (transaction input data). This is a key driver of data-availability costs for zk-rollups (Aztec, Zama, etc.) and bridges. By scanning recent blocks, the tool estimates the calldata gas share and highlights peaks and troughs that may affect proof batching costs and posting strategies.

Features
- Calculates zero/non-zero calldata bytes and estimated calldata gas per block (4/16 gas per byte model)
- Reports calldata gas as a percentage of total `gasUsed`
- Includes base fee (Gwei), tx count, and timestamps per block
- Progress output with percentage; JSON report for CI/dashboards
- Works on any EVM-compatible RPC; no ABI or contract list required

Installation
1) Python 3.9+
2) Install dependency:
   pip install web3
3) (Optional) Set a default RPC:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY

Usage
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

Expected Output
- For each block: prints block number, tx count, gasUsed, estimated calldata gas, and the percentage of gasUsed that is calldata gas.
- Summary includes:
  • Blocks analyzed
  • Average calldata gas share (%)
  • Average calldata bytes per block
  • Peak and lowest block by calldata gas share
- JSON mode outputs the per-block metrics and summary for easy thresholding in CI.

Example (truncated)
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
- **Gas Model:** Estimates based on 4 gas/zero byte and 16 gas/non-zero byte (EIP-2028).  
- **Data Availability Impact:** Higher calldata gas means greater on-chain storage cost for proofs.  
- **ZK Relevance:** Helps tune proof batching and posting strategies to minimize DA cost.  
- **EIP-4844 Compatibility:** Blobs are separate from calldata; this tool focuses on pre-blob data metrics.  
- **Reorg Safety:** Use `--from-latest` to avoid reorgs in unfinalized blocks.  
- **Automation Tip:** Run hourly with `--json` and alert if average calldata > 40%.  
- **Performance Tip:** Larger `--count` increases RPC load — use smaller samples for quick checks.  
- **Security:** The tool is read-only and safe for production use.  
- **Exit Codes:** Always returns `0`; you can evaluate “soundness” by parsing the JSON summary.  
- **Extension Idea:** Add thresholds for automatic alerts, or integrate with Grafana dashboards.  
- **Cross-Network Use:** Compare calldata trends between L1 and L2 networks to monitor scaling efficiency.  
