from flask import Flask, render_template, request, jsonify
from analysis import run_analysis

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    keyword = data.get("keyword")
    period = data.get("period")
    print(f"🧠 Received analyze request → keyword={keyword}, period={period}")

    try:
        result_html = run_analysis(keyword, period)
        print("✅ Analysis finished, returning response...")
        return jsonify({"result": result_html})
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return jsonify({"result": f"<b>Error:</b> {e}"})

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Render! Flask app is running."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render gives you a port
    app.run(host='0.0.0.0', port=port, debug=True)


import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)
