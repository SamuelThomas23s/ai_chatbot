import argparse
from summarizer import summarize_text
from keypoints import extract_key_points
from sentiment import analyze_sentiment
from file_reader import read_file
from exporter import save_to_markdown

def main():
    parser = argparse.ArgumentParser(description="AI Text Analyzer v2")
    parser.add_argument("--files", nargs="+", help="Multiple files")
    args = parser.parse_args()

    texts = []

    if args.files:
        for file in args.files:
            texts.append(read_file(file))
        text = "\n".join(texts)
    else:
        text = input("Enter your text:\n")

    print("Analyzing...\n")

    summary = summarize_text(text)
    keypoints = extract_key_points(text)
    sentiment = analyze_sentiment(text)

    print("\n--- SUMMARY ---\n", summary)
    print("\n--- KEY POINTS ---")
    for p in keypoints:
        print("-", p)

    print("\n--- SENTIMENT ---\n", sentiment)

    file_path = save_to_markdown(summary, keypoints, sentiment)
    print(f"\nSaved to: {file_path}")

if __name__ == "__main__":
    main()