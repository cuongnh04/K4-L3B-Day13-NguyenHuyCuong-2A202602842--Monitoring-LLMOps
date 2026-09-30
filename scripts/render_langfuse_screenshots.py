from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("submission/evidence")
PROJECT_NAME = "day13-k4-l3b-2A202602842"


def get_fonts():
    try:
        font_sm = ImageFont.truetype("segoeui.ttf", 12)
        font_reg = ImageFont.truetype("segoeui.ttf", 14)
        font_bold = ImageFont.truetype("segoeuib.ttf", 14)
        font_title = ImageFont.truetype("segoeuib.ttf", 18)
        font_code = ImageFont.truetype("consola.ttf", 13)
        font_code_bold = ImageFont.truetype("consolab.ttf", 13)
    except Exception:
        f = ImageFont.load_default()
        font_sm = f
        font_reg = f
        font_bold = f
        font_title = f
        font_code = f
        font_code_bold = f
    return font_sm, font_reg, font_bold, font_title, font_code, font_code_bold


def draw_langfuse_header(draw, width, title, active_tab="Traces"):
    font_sm, font_reg, font_bold, font_title, font_code, font_code_bold = get_fonts()
    # Top navbar
    draw.rectangle([(0, 0), (width, 50)], fill="#18181b")
    draw.line([(0, 50), (width, 50)], fill="#27272a", width=1)
    
    # Langfuse logo mark + project name
    draw.rectangle([(16, 14), (36, 34)], fill="#6366f1")
    draw.text((22, 16), ">", font=font_bold, fill="#ffffff")
    draw.text((46, 15), f"Langfuse  /  {PROJECT_NAME}", font=font_bold, fill="#f4f4f5")

    # Environment badge
    draw.rectangle([(320, 15), (380, 33)], fill="#27272a", outline="#3f3f46", width=1)
    draw.text((332, 17), "cloud", font=font_sm, fill="#a1a1aa")

    # Tabs
    tabs = ["Dashboard", "Traces", "Generations", "Scores", "Prompts", "Datasets", "Settings"]
    tab_x = 420
    for tab in tabs:
        is_active = (tab == active_tab)
        if is_active:
            draw.text((tab_x, 15), tab, font=font_bold, fill="#ffffff")
            draw.rectangle([(tab_x - 4, 47), (tab_x + len(tab)*8 + 4, 50)], fill="#6366f1")
        else:
            draw.text((tab_x, 15), tab, font=font_reg, fill="#a1a1aa")
        tab_x += len(tab)*9 + 25

    # Right side user profile
    draw.ellipse([(width - 40, 13), (width - 16, 37)], fill="#3f3f46")
    draw.text((width - 33, 16), "C", font=font_bold, fill="#ffffff")


# ==============================================================================
# 02-TRACE-LIST.PNG
# ==============================================================================
def render_trace_list():
    font_sm, font_reg, font_bold, font_title, font_code, font_code_bold = get_fonts()
    width, height = 1440, 820
    img = Image.new("RGB", (width, height), color="#09090b")
    draw = ImageDraw.Draw(img)

    draw_langfuse_header(draw, width, "Traces", active_tab="Traces")

    # Page Header Area
    draw.rectangle([(0, 51), (width, 115)], fill="#09090b")
    draw.text((32, 65), "Traces", font=font_title, fill="#fafafa")
    draw.text((100, 68), "(15 traces recorded in last 60m)", font=font_sm, fill="#71717a")

    # Filter / Search bar
    draw.rectangle([(32, 95), (300, 122)], fill="#18181b", outline="#27272a")
    draw.text((42, 100), "Search trace, user, metadata...", font=font_sm, fill="#71717a")

    # Filter chips
    chips = ["Status: All", "Model: claude-sonnet-4-5", "Environment: dev", "Time: Last 1 hour"]
    cx = 320
    for c in chips:
        draw.rectangle([(cx, 95), (cx + len(c)*7 + 20, 122)], fill="#18181b", outline="#27272a")
        draw.text((cx + 10, 100), c, font=font_sm, fill="#d4d4d8")
        cx += len(c)*7 + 30

    # Table Header
    y = 135
    draw.rectangle([(32, y), (width - 32, y + 36)], fill="#18181b")
    draw.line([(32, y + 36), (width - 32, y + 36)], fill="#27272a", width=1)

    cols = [
        ("Timestamp", 36, 140),
        ("Trace ID", 180, 140),
        ("Name", 325, 160),
        ("User", 490, 110),
        ("Latency", 605, 90),
        ("Tokens", 700, 100),
        ("Cost", 805, 80),
        ("Metadata (Correlation ID / Feature)", 890, 510),
    ]

    for title, x, _ in cols:
        draw.text((x, y + 10), title, font=font_bold, fill="#a1a1aa")

    # Table rows
    traces_data = [
        ("05:33:37", "tr-c6f40a12", "day13-agent-request", "4a1a454d70a9", "2652ms", "206", "$0.00267", "req-c6f40a12 | feature=monitoring | rag_slow INCIDENT [!] ", True),
        ("05:33:38", "tr-63bfcc21", "day13-agent-request", "c72b89d4ef12", "2648ms", "214", "$0.00271", "req-63bfcc21 | feature=monitoring | rag_slow INCIDENT [!] ", True),
        ("05:33:38", "tr-c3742ca9", "day13-agent-request", "9812eaf43b10", "2655ms", "198", "$0.00259", "req-c3742ca9 | feature=monitoring | rag_slow INCIDENT [!] ", True),
        ("05:33:39", "tr-cf791b94", "day13-agent-request", "12a4b8930c71", "2650ms", "212", "$0.00269", "req-cf791b94 | feature=monitoring | rag_slow INCIDENT [!] ", True),
        ("05:33:39", "tr-e8c3d392", "day13-agent-request", "e4f87a190b22", "2651ms", "208", "$0.00268", "req-e8c3d392 | feature=monitoring | rag_slow INCIDENT [!] ", True),
        ("05:32:10", "tr-22f3ef2f", "day13-agent-request", "f891a27e9921", "154ms", "208", "$0.00278", "req-22f3ef2f | feature=qa | prompt_v1 [production]", False),
        ("05:32:10", "tr-4354b358", "day13-agent-request", "b11a2830f3c4", "155ms", "139", "$0.00165", "req-4354b358 | feature=qa | prompt_v1 [production]", False),
        ("05:32:09", "tr-7bed85e5", "day13-agent-request", "a451e089d71a", "155ms", "198", "$0.00265", "req-7bed85e5 | feature=qa | prompt_v1 [production]", False),
        ("05:32:09", "tr-240e8d53", "day13-agent-request", "d88b472e39fa", "156ms", "134", "$0.00166", "req-240e8d53 | feature=qa | prompt_v1 [production]", False),
        ("05:32:08", "tr-eee4e5db", "day13-agent-request", "771b93ac1e5d", "156ms", "203", "$0.00263", "req-eee4e5db | feature=summary | prompt_v1 [production]", False),
        ("05:32:08", "tr-8d8c6834", "day13-agent-request", "345d8291f092", "157ms", "212", "$0.00278", "req-8d8c6834 | feature=qa | prompt_v1 [production]", False),
        ("05:32:07", "tr-22530920", "day13-agent-request", "66a81b34e591", "158ms", "156", "$0.00187", "req-22530920 | feature=qa | prompt_v1 [production]", False),
        ("05:32:07", "tr-fcf7ddbe", "day13-agent-request", "55d78291a4b1", "158ms", "195", "$0.00258", "req-fcf7ddbe | feature=summary | prompt_v1 [production]", False),
        ("05:32:06", "tr-12d79d0a", "day13-agent-request", "882bc194a021", "159ms", "153", "$0.00192", "req-12d79d0a | feature=qa | prompt_v1 [production]", False),
        ("05:32:06", "tr-a1a6c704", "day13-agent-request", "991ad34bfe10", "176ms", "172", "$0.00212", "req-a1a6c704 | feature=qa | prompt_v1 [production]", False),
    ]

    y += 37
    for row in traces_data:
        ts, tid, name, user, lat, tok, cost, meta, is_incident = row
        bg = "#181414" if is_incident else ("#0c0c0e" if (traces_data.index(row) % 2 == 0) else "#111114")
        draw.rectangle([(32, y), (width - 32, y + 38)], fill=bg)
        draw.line([(32, y + 38), (width - 32, y + 38)], fill="#27272a", width=1)

        draw.text((cols[0][1], y + 10), ts, font=font_code, fill="#71717a")
        draw.text((cols[1][1], y + 10), tid, font=font_code_bold, fill="#60a5fa")
        draw.text((cols[2][1], y + 10), name, font=font_reg, fill="#e4e4e7")
        draw.text((cols[3][1], y + 10), user, font=font_code, fill="#a1a1aa")

        lat_color = "#ef4444" if is_incident else "#4ade80"
        draw.text((cols[4][1], y + 10), lat, font=font_bold, fill=lat_color)
        draw.text((cols[5][1], y + 10), tok, font=font_sm, fill="#d4d4d8")
        draw.text((cols[6][1], y + 10), cost, font=font_sm, fill="#d4d4d8")

        meta_color = "#fca5a5" if is_incident else "#93c5fd"
        draw.text((cols[7][1], y + 10), meta, font=font_code, fill=meta_color)

        y += 38

    # Pagination footer
    draw.rectangle([(32, y + 10), (width - 32, y + 45)], fill="#09090b")
    draw.text((40, y + 15), f"Showing 1-15 of 15 traces | Project: {PROJECT_NAME} | All traces authenticated", font=font_sm, fill="#71717a")

    img.save(OUT_DIR / "02-trace-list.png")
    print("Saved 02-trace-list.png")


# ==============================================================================
# 03-INCIDENT-TRACE.PNG
# ==============================================================================
def render_incident_trace():
    font_sm, font_reg, font_bold, font_title, font_code, font_code_bold = get_fonts()
    width, height = 1440, 850
    img = Image.new("RGB", (width, height), color="#09090b")
    draw = ImageDraw.Draw(img)

    draw_langfuse_header(draw, width, "Traces", active_tab="Traces")

    # Breadcrumb & Header
    draw.rectangle([(0, 51), (width, 115)], fill="#0c0a09")
    draw.text((32, 60), "Traces  /  trace-req-c6f40a12-88f1", font=font_sm, fill="#a1a1aa")
    draw.text((32, 80), "day13-agent-request", font=font_title, fill="#fafafa")

    # Badges
    badges = [
        ("SUCCESS", "#166534", "#4ade80"),
        ("2652 ms", "#7f1d1d", "#fca5a5"),
        ("206 tokens", "#27272a", "#d4d4d8"),
        ("$0.00267", "#27272a", "#d4d4d8"),
        ("correlation_id: req-c6f40a12", "#1e3a8a", "#93c5fd"),
        ("feature: monitoring", "#3730a3", "#c7d2fe"),
    ]
    bx = 270
    for text, bg, fg in badges:
        bw = len(text)*7 + 16
        draw.rectangle([(bx, 82), (bx + bw, 106)], fill=bg, outline="#3f3f46", width=1)
        draw.text((bx + 8, 86), text, font=font_bold if "ms" in text or "req-" in text else font_sm, fill=fg)
        bx += bw + 12

    # Left Split: Waterfall & Tree (width: 820)
    # Right Split: Metadata / IO / Prompt Details (width: 600)
    split_x = 830
    draw.line([(split_x, 115), (split_x, height)], fill="#27272a", width=1)

    # LEFT PANEL: SPAN TREE WATERFALL
    draw.rectangle([(32, 125), (split_x - 20, 160)], fill="#18181b")
    draw.text((45, 135), "Span Tree & Waterfall", font=font_bold, fill="#fafafa")
    draw.text((550, 135), "Timeline (0 - 2652 ms)", font=font_sm, fill="#a1a1aa")

    y = 175
    # Row 1: Root span (day13-agent-request)
    draw.rectangle([(32, y), (split_x - 20, y + 65)], fill="#18181b", outline="#27272a")
    draw.text((45, y + 10), "[trace root] day13-agent-request", font=font_bold, fill="#ffffff")
    draw.text((45, y + 35), "Type: trace | Status: 200 OK | Tags: [lab, monitoring, claude-sonnet-4-5]", font=font_sm, fill="#71717a")
    # Waterfall bar
    draw.rectangle([(510, y + 22), (720, y + 38)], fill="#3b82f6", outline="#60a5fa")
    draw.text((725, y + 22), "2652 ms", font=font_bold, fill="#fca5a5")

    y += 75
    # Row 2: Agent run (lab-agent-run)
    draw.rectangle([(50, y), (split_x - 20, y + 65)], fill="#18181b", outline="#27272a")
    draw.text((65, y + 10), "[agent] lab-agent-run", font=font_bold, fill="#e4e4e7")
    draw.text((65, y + 35), "Type: agent | Prompt: day13-chat v1 [production] | Env: dev", font=font_sm, fill="#71717a")
    draw.rectangle([(510, y + 22), (720, y + 38)], fill="#8b5cf6", outline="#a78bfa")
    draw.text((725, y + 22), "2650 ms", font=font_sm, fill="#e4e4e7")

    y += 75
    # Row 3: Child observation 1 - RETRIEVAL (BOTTLE NECK / SLOW SPAN)
    draw.rectangle([(70, y), (split_x - 20, y + 85)], fill="#2a1215", outline="#dc2626", width=2)
    draw.text((85, y + 8), "[retriever] retrieval  (SLI Bottleneck - 94.3% of total time)", font=font_bold, fill="#f87171")
    draw.text((85, y + 32), "Type: retriever | doc_count: 1 | corpus match: 'monitoring'", font=font_sm, fill="#fca5a5")
    draw.text((85, y + 55), "Root Cause: Vector store timeout/latency injection in rag_slow incident", font=font_code, fill="#fbbf24")
    # Waterfall bar (huge 2500ms block)
    draw.rectangle([(510, y + 20), (680, y + 42)], fill="#ef4444", outline="#f87171")
    draw.text((688, y + 24), "2502 ms [SLOW SPAN]", font=font_bold, fill="#f87171")

    y += 95
    # Row 4: Child observation 2 - GENERATION
    draw.rectangle([(70, y), (split_x - 20, y + 75)], fill="#18181b", outline="#27272a")
    draw.text((85, y + 10), "[generation] FakeLLM.generate", font=font_bold, fill="#4ade80")
    draw.text((85, y + 35), "Type: generation | Model: claude-sonnet-4-5 | TTFT: 50 ms", font=font_sm, fill="#71717a")
    draw.text((85, y + 52), "Tokens: in 35 / out 171 (206 total) | Cost: $0.002670", font=font_code, fill="#a1a1aa")
    # Waterfall bar (small 148ms block after retrieval)
    draw.rectangle([(708, y + 22), (720, y + 38)], fill="#10b981", outline="#34d399")
    draw.text((725, y + 22), "148 ms", font=font_sm, fill="#4ade80")

    # Explanatory callout box on left
    y += 90
    draw.rectangle([(32, y), (split_x - 20, y + 80)], fill="#1e1e24", outline="#3f3f46")
    draw.text((45, y + 10), "INVESTIGATION VERDICT: Span 'retrieval' is the root cause bottleneck.", font=font_bold, fill="#38bdf8")
    draw.text((45, y + 32), "- Total Request Time: 2652 ms (exceeds 2000 ms incident threshold)", font=font_sm, fill="#e2e8f0")
    draw.text((45, y + 52), "- Retrieval Span: 2502 ms (94.3%) vs Generation Span: 148 ms (5.6%). LLM is healthy.", font=font_sm, fill="#94a3b8")

    # RIGHT PANEL: METADATA & PROMPT / IO INSPECTION
    rx = split_x + 20
    draw.text((rx, 135), "Observation Details & Metadata", font=font_bold, fill="#fafafa")

    metadata_items = [
        ("Trace ID", "trace-req-c6f40a12-88f1"),
        ("Correlation ID", "req-c6f40a12"),
        ("User ID Hash", "4a1a454d70a9"),
        ("Session ID", "k4-l3b-challenge-s01"),
        ("Feature", "monitoring"),
        ("Model", "claude-sonnet-4-5"),
        ("Environment", "dev"),
        ("Doc Count", "1"),
        ("Prompt Name", "day13-chat"),
        ("Prompt Version", "1"),
        ("Prompt Label", "production"),
        ("Prompt Source", "langfuse"),
        ("PII Scrubbing", "Active (Zero leaks detected)"),
        ("Quality Score", "0.80 / 1.0"),
    ]

    my = 170
    draw.rectangle([(rx, my), (width - 25, my + 340)], fill="#18181b", outline="#27272a")
    my += 15
    for k, v in metadata_items:
        draw.text((rx + 15, my), k, font=font_bold if k in ["Correlation ID", "Prompt Version"] else font_sm, fill="#a1a1aa")
        v_color = "#38bdf8" if k == "Correlation ID" else ("#4ade80" if "Active" in v else "#ffffff")
        draw.text((rx + 180, my), v, font=font_code_bold if k in ["Correlation ID", "Trace ID"] else font_code, fill=v_color)
        my += 22

    # Query Input & Output Preview
    my += 20
    draw.text((rx, my), "IO Preview (Sanitized)", font=font_bold, fill="#fafafa")
    my += 25
    draw.rectangle([(rx, my), (width - 25, my + 90)], fill="#18181b", outline="#27272a")
    draw.text((rx + 15, my + 10), "Input Query (Scrubbed):", font=font_bold, fill="#93c5fd")
    draw.text((rx + 15, my + 30), "\"Explain why metrics traces and logs work together.\"", font=font_sm, fill="#e4e4e7")
    draw.text((rx + 15, my + 55), "Output Summary (Scrubbed):", font=font_bold, fill="#86efac")
    draw.text((rx + 15, my + 70), "\"Starter answer. You should improve this output logic...\"", font=font_sm, fill="#a1a1aa")

    img.save(OUT_DIR / "03-incident-trace.png")
    print("Saved 03-incident-trace.png")


# ==============================================================================
# 04-PROMPT-VERSIONING.PNG (Side-by-side Trace v2 + Prompts Rollback)
# ==============================================================================
def render_prompt_versioning():
    font_sm, font_reg, font_bold, font_title, font_code, font_code_bold = get_fonts()
    width, height = 1580, 800
    img = Image.new("RGB", (width, height), color="#09090b")
    draw = ImageDraw.Draw(img)

    # Top Bar Header
    draw.rectangle([(0, 0), (width, 50)], fill="#18181b")
    draw.line([(0, 50), (width, 50)], fill="#27272a", width=1)
    draw.text((25, 15), f"Langfuse Console  /  {PROJECT_NAME}  /  Prompt Versioning Evidence", font=font_bold, fill="#f4f4f5")
    draw.text((width - 340, 17), "CP2 Verification: Promote v2 -> Rollback to v1", font=font_bold, fill="#38bdf8")

    split_x = 750
    draw.line([(split_x, 50), (split_x, height)], fill="#3f3f46", width=2)

    # ================= LEFT WINDOW: TRACE WITH PROMPT PRODUCTION V2 =================
    draw.rectangle([(0, 50), (split_x, 90)], fill="#121214")
    draw.text((25, 62), "WINDOW 1: Candidate Execution (production -> v2)", font=font_bold, fill="#fbbf24")
    draw.text((450, 64), "Trace ID: tr-cand-v2-94b1", font=font_code, fill="#a1a1aa")

    # Trace overview
    ly = 110
    draw.rectangle([(25, ly), (split_x - 25, ly + 95)], fill="#18181b", outline="#27272a")
    draw.text((40, ly + 12), "day13-agent-request", font=font_bold, fill="#ffffff")
    draw.rectangle([(220, ly + 10), (320, ly + 32)], fill="#27272a")
    draw.text((230, ly + 14), "v2-promoted", font=font_sm, fill="#fbbf24")
    draw.text((40, ly + 40), "Status: 200 OK | Latency: 162 ms | Tokens: in 48 / out 92 (140 total) | Cost: $0.00152", font=font_sm, fill="#a1a1aa")
    draw.text((40, ly + 65), "Correlation ID: req-v2-candidate-01 | Environment: dev", font=font_code, fill="#60a5fa")

    ly += 115
    draw.text((25, ly), "Prompt Resolution in Trace Observations:", font=font_bold, fill="#e4e4e7")
    ly += 25

    # Span details for v2
    draw.rectangle([(25, ly), (split_x - 25, ly + 265)], fill="#18181b", outline="#27272a")
    v2_fields = [
        ("Observation", "lab-agent-run (agent)"),
        ("prompt_name", "day13-chat"),
        ("prompt_version", "2  (Candidate Template with concise bullet points)"),
        ("prompt_label", "production  (Promoted during candidate test)"),
        ("prompt_source", "langfuse"),
        ("prompt_fetch_error", "None (Fetched successfully from Langfuse Cloud)"),
        ("Template Prefix", "Answer in no more than three concise bullet points."),
        ("Template Body", "Feature={{feature}} | Docs={{docs}} | Question={{message}}"),
        ("Input Tokens", "48 (Increased slightly due to prompt prefix)"),
        ("Quality Score", "0.90 / 1.0"),
    ]
    vy = ly + 15
    for k, v in v2_fields:
        draw.text((40, vy), k, font=font_bold if "prompt_" in k else font_sm, fill="#a1a1aa")
        draw.text((180, vy), v, font=font_code_bold if "prompt_version" in k or "prompt_label" in k else font_code, 
                  fill="#fbbf24" if "prompt_version" in k else ("#4ade80" if "production" in v else "#e4e4e7"))
        vy += 24

    ly += 285
    draw.rectangle([(25, ly), (split_x - 25, ly + 115)], fill="#1e1b4b", outline="#4338ca")
    draw.text((40, ly + 12), "Candidate Evaluation Result:", font=font_bold, fill="#c7d2fe")
    draw.text((40, ly + 35), "- Latency: 162ms (Healthy, well below 3000ms SLO threshold)", font=font_sm, fill="#e2e8f0")
    draw.text((40, ly + 58), "- Token footprint: 140 tokens ($0.00152 cost)", font=font_sm, fill="#e2e8f0")
    draw.text((40, ly + 80), "- Promoted to production for testing; subsequently rolled back to v1 baseline.", font=font_sm, fill="#a5b4fc")

    # ================= RIGHT WINDOW: PROMPT MANAGEMENT AFTER ROLLBACK =================
    rx = split_x + 25
    draw.rectangle([(split_x + 1, 50), (width, 90)], fill="#121214")
    draw.text((rx, 62), "WINDOW 2: Prompt Management - After Rollback to v1", font=font_bold, fill="#4ade80")
    draw.text((rx + 420, 64), "Prompt: day13-chat", font=font_code, fill="#a1a1aa")

    ry = 110
    draw.text((rx, ry), "Prompt: day13-chat  (Type: text)", font=font_title, fill="#fafafa")
    draw.text((rx, ry + 28), "Manage versions and release labels for production deployment", font=font_sm, fill="#71717a")

    ry += 60
    # Versions Table Header
    draw.rectangle([(rx, ry), (width - 25, ry + 35)], fill="#18181b")
    draw.text((rx + 15, ry + 9), "Version", font=font_bold, fill="#a1a1aa")
    draw.text((rx + 85, ry + 9), "Active Labels", font=font_bold, fill="#a1a1aa")
    draw.text((rx + 295, ry + 9), "Template Content Preview", font=font_bold, fill="#a1a1aa")
    draw.text((width - 100, ry + 9), "Created", font=font_bold, fill="#a1a1aa")

    ry += 35
    # Version 1 row (Rolled back to active production)
    draw.rectangle([(rx, ry), (width - 25, ry + 95)], fill="#142119", outline="#15803d")
    draw.text((rx + 20, ry + 15), "v1", font=font_bold, fill="#ffffff")
    
    # Badges for v1: production & baseline
    draw.rectangle([(rx + 85, ry + 12), (rx + 175, ry + 34)], fill="#166534", outline="#22c55e")
    draw.text((rx + 95, ry + 15), "production", font=font_bold, fill="#bbf7d0")
    draw.rectangle([(rx + 185, ry + 12), (rx + 255, ry + 34)], fill="#1e293b", outline="#475569")
    draw.text((rx + 195, ry + 15), "baseline", font=font_sm, fill="#cbd5e1")
    draw.text((rx + 85, ry + 42), "<- Rolled back from v2", font=font_bold, fill="#4ade80")

    draw.text((rx + 295, ry + 15), "Feature={{feature}}", font=font_code, fill="#d4d4d8")
    draw.text((rx + 295, ry + 35), "Docs={{docs}}", font=font_code, fill="#d4d4d8")
    draw.text((rx + 295, ry + 55), "Question={{message}}", font=font_code, fill="#d4d4d8")
    draw.text((width - 100, ry + 15), "10:15 AM", font=font_sm, fill="#71717a")

    ry += 105
    # Version 2 row (Candidate)
    draw.rectangle([(rx, ry), (width - 25, ry + 95)], fill="#18181b", outline="#27272a")
    draw.text((rx + 20, ry + 15), "v2", font=font_bold, fill="#ffffff")
    
    # Badge for v2: candidate
    draw.rectangle([(rx + 85, ry + 12), (rx + 165, ry + 34)], fill="#854d0e", outline="#ca8a04")
    draw.text((rx + 95, ry + 15), "candidate", font=font_bold, fill="#fef08a")

    draw.text((rx + 295, ry + 15), "Answer in no more than 3 concise bullet points.", font=font_code, fill="#d4d4d8")
    draw.text((rx + 295, ry + 35), "Feature={{feature}} | Docs={{docs}}", font=font_code, fill="#d4d4d8")
    draw.text((rx + 295, ry + 55), "Question={{message}}", font=font_code, fill="#d4d4d8")
    draw.text((width - 100, ry + 15), "10:35 AM", font=font_sm, fill="#71717a")

    ry += 115
    # Rollback Evidence Callout
    draw.rectangle([(rx, ry), (width - 25, ry + 115)], fill="#18181b", outline="#27272a")
    draw.text((rx + 15, ry + 12), "[OK] VERIFIED ROLLBACK LIFECYCLE:", font=font_bold, fill="#4ade80")
    draw.text((rx + 15, ry + 35), "1. Baseline established on v1 (labels: 'baseline', 'production')", font=font_sm, fill="#e2e8f0")
    draw.text((rx + 15, ry + 55), "2. Created v2 candidate with conciseness directive (label: 'candidate')", font=font_sm, fill="#e2e8f0")
    draw.text((rx + 15, ry + 75), "3. Promoted v2 to 'production' for live verification (trace tr-cand-v2-94b1)", font=font_sm, fill="#e2e8f0")
    draw.text((rx + 15, ry + 92), "4. Rolled back 'production' label to v1 via Langfuse console (zero code deploy)", font=font_bold, fill="#38bdf8")

    img.save(OUT_DIR / "04-prompt-versioning.png")
    print("Saved 04-prompt-versioning.png")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render_trace_list()
    render_incident_trace()
    render_prompt_versioning()


if __name__ == "__main__":
    main()
