from flask import Flask, request, jsonify
from summarizer import summarize_text
from keypoints import extract_key_points
from sentiment import analyze_sentiment

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    summary = summarize_text(text)
    keypoints = extract_key_points(text)
    sentiment = analyze_sentiment(text)

    return jsonify({
        "summary": summary,
        "keypoints": keypoints,
        "sentiment": sentiment
    })

if __name__ == "__main__":
    app.run(debug=True)