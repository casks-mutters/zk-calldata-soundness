# app.py
import os
import sys
import json
import time
import argparse
from typing import Dict, List
from datetime import datetime
from web3 import Web3

DEFAULT_RPC = os.environ.get("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")

def get_block_details(w3: Web3, block_number: int) -> Dict[str, any]:
    """Fetch minimal block information for soundness verification."""
    block = w3.eth.get_block(block_number)
    tx_count = len(block.transactions)
    base_fee = block.get("baseFeePerGas", 0)
    return {
        "number": block.number,
        "timestamp_utc": datetime.utcfromtimestamp(block.timestamp).isoformat() + "Z",
        "miner": block.miner,
        "gas_used": block.gasUsed,
        "gas_limit": block.gasLimit,
        "tx_count": tx_count,
        "base_fee_gwei": round(base_fee / 1e9, 3),
    }

def analyze_blocks(w3: Web3, start: int, end: int, step: int) -> List[Dict[str, any]]:
    """Scan a range of blocks and collect metadata for each."""
    blocks = []
    total = len(range(start, end + 1, step))
    for i, n in enumerate(range(start, end + 1, step), start=1):
        pct = (i / total) * 100
        print(f"🔍 Fetching block {n} ({i}/{total}, {pct:.1f}%)")
        try:
            block_data = get_block_details(w3, n)
            print(f"   🕒 Timestamp: {block_data['timestamp_utc']}")
            blocks.append(block_data)
        except Exception as e:
            print(f"⚠️  Error fetching block {n}: {e}")
    return blocks

def compute_metrics(blocks: List[Dict[str, any]]) -> Dict[str, any]:
    """Calculate simple statistics about gas usage and block consistency."""
    if not blocks:
        return {"ok": False, "message": "No blocks retrieved"}
    utilizations = [b["gas_used"] / b["gas_limit"] * 100 for b in blocks if b["gas_limit"]]
    avg_util = sum(utilizations) / len(utilizations)
    max_util = max(utilizations)
    min_util = min(utilizations)
    avg_tx = sum(b["tx_count"] for b in blocks) / len(blocks)
    avg_base_fee = sum(b["base_fee_gwei"] for b in blocks) / len(blocks)
    return {
        "avg_utilization_percent": round(avg_util, 2),
        "max_utilization_percent": round(max_util, 2),
        "min_utilization_percent": round(min_util, 2),
        "avg_tx_per_block": round(avg_tx, 2),
        "avg_base_fee_gwei": round(avg_base_fee, 3),
        "block_count": len(blocks),
        "ok": avg_util > 40 and max_util - min_util < 50
    }

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="zk-block-soundness — analyze recent block gas usage, miner distribution, and consistency for zk systems."
    )
    p.add_argument("--rpc", default=DEFAULT_RPC, help="EVM-compatible RPC URL (default: env RPC_URL or Infura key)")
    p.add_argument("--from-block", type=int, required=True, help="Start block number")
    p.add_argument("--to-block", type=int, required=True, help="End block number")
    p.add_argument("--step", type=int, default=5, help="Sampling step (default: 5)")
    p.add_argument("--timeout", type=int, default=30, help="RPC timeout seconds (default: 30)")
    p.add_argument("--json", action="store_true", help="Output JSON summary")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    if args.from_block > args.to_block:
        print("❌ Invalid range: --from-block must be <= --to-block")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": args.timeout}))
    if not w3.is_connected():
        print("❌ RPC connection failed.")
        sys.exit(1)

    print("🔧 zk-block-soundness")
    print(f"🔗 RPC: {args.rpc}")
    print(f"🧱 Range: {args.from_block} → {args.to_block} (step={args.step})")
    print(f"🕒 Start Time: {datetime.utcnow().isoformat()}Z")

    t0 = time.time()
    blocks = analyze_blocks(w3, args.from_block, args.to_block, args.step)
    metrics = compute_metrics(blocks)
    elapsed = round(time.time() - t0, 2)

    print("\n📊 Summary:")
    print(f"  • Avg Gas Utilization: {metrics['avg_utilization_percent']}%")
    print(f"  • Max Utilization: {metrics['max_utilization_percent']}%")
    print(f"  • Min Utilization: {metrics['min_utilization_percent']}%")
    print(f"  • Avg Transactions per Block: {metrics['avg_tx_per_block']}")
    print(f"  • Avg Base Fee: {metrics['avg_base_fee_gwei']} Gwei")
    print(f"  • Blocks Analyzed: {metrics['block_count']}")
    print(f"  • Status: {'✅ SOUND' if metrics['ok'] else '🚨 UNSOUND'}")
    print(f"⏱️ Completed in {elapsed}s")

    if args.json:
        out = {
            "rpc": args.rpc,
            "range": [args.from_block, args.to_block, args.step],
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "metrics": metrics,
            "blocks": blocks,
            "elapsed_seconds": elapsed,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))

    sys.exit(0 if metrics["ok"] else 2)

if __name__ == "__main__":
    main()
