import json
import math
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

LOG_PATH = Path("data/logs.jsonl")
OUT_PATH = Path("submission/evidence/05-dashboard-incident.png")


def parse_logs(path: Path):
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def main():
    records = parse_logs(LOG_PATH)
    if not records:
        print("No records found in data/logs.jsonl")
        return

    # Filter events
    resp_records = [r for r in records if r.get("event") == "response_sent"]
    req_records = [r for r in records if r.get("event") == "request_received"]
    err_records = [r for r in records if r.get("event") == "request_failed"]

    # Compute metrics
    latencies = [r.get("latency_ms", 0) for r in resp_records]
    ttfts = [r.get("ttft_ms", 0) for r in resp_records]
    costs = [r.get("cost_usd", 0.0) for r in resp_records]
    tokens_in = [r.get("tokens_in", 0) for r in resp_records]
    tokens_out = [r.get("tokens_out", 0) for r in resp_records]
    qualities = [r.get("quality_score", 0.0) for r in resp_records]
    
    # Calculate percentiles
    def pctl(arr, q):
        if not arr:
            return 0
        s = sorted(arr)
        idx = min(len(s) - 1, max(0, int(math.ceil(q / 100.0 * len(s))) - 1))
        return s[idx]

    p50 = pctl(latencies, 50)
    p95 = pctl(latencies, 95)
    p99 = pctl(latencies, 99)
    ttft_p95 = pctl(ttfts, 95)

    total_requests = len(req_records)
    total_responses = len(resp_records)
    total_errors = len(err_records)
    error_rate = (total_errors / total_requests * 100) if total_requests else 0.0
    tool_successes = sum(1 for r in resp_records if r.get("tool_success") is True)
    tool_total = total_responses + total_errors
    tool_success_rate = (tool_successes / tool_total * 100) if tool_total else 100.0

    total_cost = sum(costs)
    sum_tokens_in = sum(tokens_in)
    sum_tokens_out = sum(tokens_out)
    avg_quality = (sum(qualities) / len(qualities)) if qualities else 0.0

    # Plot styling - Dark Theme
    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 2, figsize=(16, 12), dpi=120)
    fig.patch.set_facecolor("#0f172a")

    title_text = (
        "K4-L3B Day 13 Monitoring & LLMOps — System Health Dashboard\n"
        f"Window: Last 60m | Refresh: 30s | MSSV: 2A202602842 | Incident: rag_slow"
    )
    fig.suptitle(title_text, fontsize=16, fontweight="bold", color="#38bdf8", y=0.98)

    # Palette
    accent_blue = "#38bdf8"
    accent_green = "#4ade80"
    accent_red = "#f87171"
    accent_amber = "#fbbf24"
    accent_purple = "#c084fc"
    card_bg = "#1e293b"
    grid_color = "#334155"

    for ax in axes.flat:
        ax.set_facecolor(card_bg)
        ax.grid(True, linestyle="--", alpha=0.5, color=grid_color)
        ax.tick_params(colors="#94a3b8")
        for spine in ax.spines.values():
            spine.set_color("#475569")

    # 1. LATENCY PANEL
    ax1 = axes[0, 0]
    ax1.set_title("1. Latency Percentiles & TTFT (unit: ms)", fontsize=12, fontweight="bold", color="#f1f5f9")
    req_indices = list(range(1, len(latencies) + 1))
    ax1.plot(req_indices, latencies, color=accent_amber, marker="o", label="Latency (ms)", linewidth=2)
    ax1.plot(req_indices, ttfts, color=accent_green, linestyle=":", marker="x", label="TTFT (ms)", linewidth=1.5)
    ax1.axhline(3000, color=accent_red, linestyle="--", linewidth=1.5, label="Threshold SLO (<=3000ms)")
    ax1.set_xlabel("Request Sequence", color="#94a3b8")
    ax1.set_ylabel("Latency (ms)", color="#94a3b8")
    ax1.legend(loc="upper left", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    summary_latency = f"P50: {p50}ms | P95: {p95}ms | P99: {p99}ms | TTFT P95: {ttft_p95}ms"
    ax1.text(0.98, 0.05, summary_latency, transform=ax1.transAxes, fontsize=9, color="#e2e8f0",
             ha="right", bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    # 2. TRAFFIC PANEL
    ax2 = axes[0, 1]
    ax2.set_title("2. Request Traffic (unit: requests_per_minute)", fontsize=12, fontweight="bold", color="#f1f5f9")
    # Histogram of requests over sequence
    ax2.bar(req_indices, [1]*len(req_indices), color=accent_blue, width=0.6, label="Requests", alpha=0.8)
    ax2.axhline(1, color=accent_green, linestyle="--", linewidth=1.5, label="Threshold (>= 1 rpm)")
    ax2.set_xlabel("Request Sequence", color="#94a3b8")
    ax2.set_ylabel("Traffic Count", color="#94a3b8")
    ax2.legend(loc="upper right", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    ax2.text(0.98, 0.15, f"Total Requests: {total_requests}\nRate: ~{len(req_indices)} req/window",
             transform=ax2.transAxes, fontsize=9, color="#e2e8f0", ha="right",
             bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    # 3. ERRORS & RETRIEVAL SUCCESS PANEL
    ax3 = axes[1, 0]
    ax3.set_title("3. Error Rate & Retrieval Success (unit: percent)", fontsize=12, fontweight="bold", color="#f1f5f9")
    bars = ax3.bar(["Error Rate %", "Retrieval Success %"], [error_rate, tool_success_rate],
                   color=[accent_red if error_rate > 2 else accent_green, accent_blue], width=0.4)
    ax3.axhline(2.0, color=accent_red, linestyle="--", linewidth=1.5, label="Max Error Rate Threshold (<= 2%)")
    ax3.axhline(90.0, color=accent_green, linestyle=":", linewidth=1.5, label="Min Retrieval Success (>= 90%)")
    ax3.set_ylim(0, 105)
    ax3.set_ylabel("Percentage (%)", color="#94a3b8")
    ax3.legend(loc="lower left", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    for bar in bars:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., h + 2, f"{h:.1f}%", ha="center", va="bottom", color="#f1f5f9", fontweight="bold")
    ax3.text(0.98, 0.70, f"Failures: {total_errors}\nRetrieval OK: {tool_successes}/{tool_total}",
             transform=ax3.transAxes, fontsize=9, color="#e2e8f0", ha="right",
             bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    # 4. COST PANEL
    ax4 = axes[1, 1]
    ax4.set_title("4. Cost Over Time (unit: USD)", fontsize=12, fontweight="bold", color="#f1f5f9")
    cum_cost = []
    c_acc = 0.0
    for c in costs:
        c_acc += c
        cum_cost.append(c_acc)
    ax4.plot(req_indices, cum_cost, color=accent_purple, marker="s", label="Cumulative Cost ($)", linewidth=2)
    ax4.axhline(2.5, color=accent_red, linestyle="--", linewidth=1.5, label="Daily Budget Threshold (<= $2.50)")
    ax4.set_xlabel("Request Sequence", color="#94a3b8")
    ax4.set_ylabel("USD ($)", color="#94a3b8")
    ax4.legend(loc="upper left", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    ax4.text(0.98, 0.15, f"Total Spent: ${total_cost:.5f}\nPer-req Avg: ${total_cost/max(1, len(costs)):.5f}",
             transform=ax4.transAxes, fontsize=9, color="#e2e8f0", ha="right",
             bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    # 5. TOKENS PANEL
    ax5 = axes[2, 0]
    ax5.set_title("5. Input & Output Tokens (unit: tokens)", fontsize=12, fontweight="bold", color="#f1f5f9")
    ax5.bar(req_indices, tokens_in, label="Input Tokens", color="#3b82f6", alpha=0.8, width=0.4, align="edge")
    ax5.bar([i + 0.4 for i in req_indices], tokens_out, label="Output Tokens", color="#ec4899", alpha=0.8, width=0.4, align="edge")
    ax5.set_xlabel("Request Sequence", color="#94a3b8")
    ax5.set_ylabel("Token Count", color="#94a3b8")
    ax5.legend(loc="upper left", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    ax5.text(0.98, 0.70, f"Total In: {sum_tokens_in}\nTotal Out: {sum_tokens_out}\nTotal: {sum_tokens_in+sum_tokens_out}",
             transform=ax5.transAxes, fontsize=9, color="#e2e8f0", ha="right",
             bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    # 6. QUALITY PANEL
    ax6 = axes[2, 1]
    ax6.set_title("6. Quality Proxy (unit: score_0_to_1)", fontsize=12, fontweight="bold", color="#f1f5f9")
    ax6.plot(req_indices, qualities, color=accent_green, marker="^", label="Quality Score", linewidth=2)
    ax6.axhline(0.75, color=accent_red, linestyle="--", linewidth=1.5, label="Quality Threshold (>= 0.75)")
    ax6.set_ylim(0, 1.05)
    ax6.set_xlabel("Request Sequence", color="#94a3b8")
    ax6.set_ylabel("Quality Score (0.0 - 1.0)", color="#94a3b8")
    ax6.legend(loc="lower left", facecolor=card_bg, edgecolor=grid_color, fontsize=8)
    ax6.text(0.98, 0.15, f"Mean Quality: {avg_quality:.2f} / 1.0\nStatus: {'HEALTHY' if avg_quality >= 0.75 else 'DEGRADED'}",
             transform=ax6.transAxes, fontsize=9, color="#e2e8f0", ha="right",
             bbox=dict(boxstyle="round", facecolor="#334155", alpha=0.8))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PATH, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Successfully generated dashboard to {OUT_PATH}")


if __name__ == "__main__":
    main()
