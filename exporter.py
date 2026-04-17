import os
from datetime import datetime

def save_to_markdown(summary, keypoints, sentiment):
    os.makedirs("outputs", exist_ok=True)

    filename = f"outputs/result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# AI Text Analysis\n\n")

        f.write("## Summary\n")
        f.write(summary + "\n\n")

        f.write("## Key Points\n")
        for point in keypoints:
            f.write(f"- {point}\n")

        f.write("\n## Sentiment\n")
        f.write(sentiment + "\n")

    return filename