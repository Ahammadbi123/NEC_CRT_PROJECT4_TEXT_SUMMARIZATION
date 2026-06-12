from flask import Flask, render_template, request, jsonify
from groq import Groq
from flask import send_file
from reportlab.pdfgen import canvas
import os
import io
from textwrap import wrap
app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():

    try:
        text = request.json["text"]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
            "content": f"""
Summarize the following text in a concise and professional manner.
Focus only on the key ideas, remove repetitive details,
and generate a well-structured abstract of about 120-150 words.

Text:
{text}
"""
                }
            ],
            temperature=0.3,
            max_tokens=300
        )

        summary_text = completion.choices[0].message.content

        return jsonify({"summary": summary_text})

    except Exception as e:
        print(f"GROQ ERROR: {str(e)}")
        return jsonify({"error": f"AI Error: {str(e)}"}), 500
    
@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    data = request.get_json()
    summary = data.get("summary", "")

    pdf_buffer = io.BytesIO()

    p = canvas.Canvas(pdf_buffer)

    p.setTitle("Summary Report")

    p.drawString(50, 800, "AI Smart Summarizer")
    p.drawString(50, 780, "Summary Report")

    y = 740

    for paragraph in summary.split("\n"):

      wrapped_lines = wrap(paragraph, width=90)

    for line in wrapped_lines:

        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 11)
            y = 800

        p.drawString(50, y, line)
        y -= 18

    y -= 10

    p.save()

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="Summary_Report.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)