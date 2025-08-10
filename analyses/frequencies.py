TITLE = "Top Numbers by Frequency"
ORDER = 20

def generate(df):
    counts = {}
    for i in range(1,7):
        for n in df[f"Num{i}"]:
            counts[n] = counts.get(n, 0) + 1
    top = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:20]
    lines = [f"## {TITLE}", "", "| Number | Count |", "|---:|---:|"]
    lines += [f"| {n} | {c} |" for n, c in top]
    lines.append("")
    return "\n".join(lines)
