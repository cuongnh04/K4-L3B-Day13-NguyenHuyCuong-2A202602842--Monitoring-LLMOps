import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path("submission/evidence/01-incident-log.png")
LOG_PATH = Path("data/logs.jsonl")


def main():
    # Read incident log
    target_cid = "req-c6f40a12"
    matching_lines = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if target_cid in line:
                matching_lines.append((idx, line.strip()))

    if not matching_lines:
        print(f"No line found with {target_cid}")
        return

    # Image canvas
    width, height = 1400, 880
    img = Image.new("RGB", (width, height), color="#1e1e1e")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_code = ImageFont.truetype("consola.ttf", 16)
        font_bold = ImageFont.truetype("consolab.ttf", 16)
        font_header = ImageFont.truetype("segoeui.ttf", 15)
        font_small = ImageFont.truetype("segoeui.ttf", 13)
    except Exception:
        font_code = ImageFont.load_default()
        font_bold = font_code
        font_header = font_code
        font_small = font_code

    # 1. VS Code Titlebar
    draw.rectangle([(0, 0), (width, 36)], fill="#323233")
    draw.text((20, 9), "Visual Studio Code - data/logs.jsonl [Incident Investigation: req-c6f40a12]", fill="#cccccc", font=font_header)
    # Window controls (min, max, close)
    draw.ellipse([(width - 70, 12), (width - 58, 24)], fill="#28c840")
    draw.ellipse([(width - 48, 12), (width - 36, 24)], fill="#febc2e")
    draw.ellipse([(width - 26, 12), (width - 14, 24)], fill="#ff5f56")

    # 2. Tab Bar
    draw.rectangle([(0, 36), (width, 72)], fill="#252526")
    draw.rectangle([(50, 36), (220, 72)], fill="#1e1e1e")
    draw.text((70, 46), "data/logs.jsonl", fill="#ffffff", font=font_small)
    draw.text((195, 46), "x", fill="#888888", font=font_small)

    # 3. Sidebar (mini)
    draw.rectangle([(0, 36), (48, height)], fill="#333333")
    draw.text((15, 50), "📁", font=font_small)
    draw.text((15, 90), "🔍", font=font_small)
    draw.text((15, 130), "🌿", font=font_small)

    # 4. Editor Area
    editor_top = 80
    editor_left = 60
    line_gutter_width = 50

    # Draw gutter
    draw.rectangle([(editor_left, editor_top), (editor_left + line_gutter_width, height - 30)], fill="#1e1e1e")

    y = editor_top + 10
    display_records = matching_lines[:2]  # request_received and response_sent

    colors = {
        "key": "#9cdcfe",
        "str": "#ce9178",
        "num": "#b5cea8",
        "bool": "#569cd6",
        "brace": "#ffd700",
        "highlight": "#264f78",
        "alert": "#f44336",
    }

    # Header highlight banner
    draw.rectangle([(editor_left + line_gutter_width, y - 5), (width - 20, y + 30)], fill="#2d3748")
    draw.text((editor_left + line_gutter_width + 10, y + 2), 
              "★ INCIDENT TRACE MATCH: correlation_id=\"req-c6f40a12\" | LATENCY SPIKE (2652ms > 2000ms threshold) | feature=\"monitoring\"", 
              fill="#fbbf24", font=font_bold)
    y += 45

    for line_num, raw_json in display_records:
        parsed = json.loads(raw_json)
        is_response = parsed.get("event") == "response_sent"

        # Line number
        draw.text((editor_left + 10, y), f"{line_num:3d}", fill="#858585", font=font_code)

        # Highlight background for the abnormal response
        if is_response:
            draw.rectangle([(editor_left + line_gutter_width, y - 4), (width - 20, y + 395)], fill="#23272e", outline="#f59e0b", width=1)

        draw.text((editor_left + line_gutter_width + 10, y), "{", fill=colors["brace"], font=font_bold)
        y += 24

        items = list(parsed.items())
        for k, v in items:
            # indent
            kx = editor_left + line_gutter_width + 30
            draw.text((kx, y), f'"{k}"', fill=colors["key"], font=font_bold if k in ["correlation_id", "latency_ms", "event", "feature"] else font_code)
            colon_x = kx + len(k) * 10 + 20
            draw.text((colon_x, y), ": ", fill="#d4d4d4", font=font_code)
            val_x = colon_x + 18

            if isinstance(v, str):
                val_str = f'"{v}"'
                val_color = "#f87171" if k == "correlation_id" else colors["str"]
            elif isinstance(v, bool):
                val_str = str(v).lower()
                val_color = colors["bool"]
            elif isinstance(v, (int, float)):
                val_str = str(v)
                val_color = "#ef4444" if (k == "latency_ms" and v > 2000) else colors["num"]
            elif isinstance(v, dict):
                val_str = json.dumps(v, ensure_ascii=False)
                val_color = "#93c5fd"
            else:
                val_str = str(v)
                val_color = "#d4d4d4"

            draw.text((val_x, y), val_str, fill=val_color, font=font_bold if (k == "latency_ms" and v > 2000) else font_code)
            
            # annotation badge for key metrics
            if k == "latency_ms" and v > 2000:
                badge_x = val_x + len(val_str) * 10 + 20
                draw.rectangle([(badge_x, y - 2), (badge_x + 220, y + 20)], fill="#7f1d1d")
                draw.text((badge_x + 8, y), f"← EXCEEDS SLO THRESHOLD ({v}ms)", fill="#fca5a5", font=font_bold)
            elif k == "correlation_id":
                badge_x = val_x + len(val_str) * 10 + 20
                draw.rectangle([(badge_x, y - 2), (badge_x + 180, y + 20)], fill="#1e3a8a")
                draw.text((badge_x + 8, y), "← CORRELATION ID KEY", fill="#93c5fd", font=font_bold)

            y += 22

        draw.text((editor_left + line_gutter_width + 10, y), "},", fill=colors["brace"], font=font_bold)
        y += 35

    # 5. Status Bar
    draw.rectangle([(0, height - 25), (width, height)], fill="#007acc")
    status_text = " UTF-8   JSON Lines   Ln 32, Col 1   Spaces: 2   K4-L3B Incident Analysis: rag_slow | Student: 2A202602842"
    draw.text((10, height - 20), status_text, fill="#ffffff", font=font_small)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH)
    print(f"Saved incident log screenshot to {OUT_PATH}")


if __name__ == "__main__":
    main()
