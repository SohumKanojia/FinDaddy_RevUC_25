from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Set up Gemini AI API Key
genai.configure(api_key="AIzaSyANVbXSdfL63j-6vNm-jyDEZCtlbCCeMHQ")
model = genai.GenerativeModel("gemini-pro")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Check if the question is about compound interest
    if "compound interest" in user_message.lower():
        # Respond with a general explanation
        response_text = (
            "Compound interest is the process where interest is added to the principal sum, "
            "and from that moment on, interest is earned on the new total amount. "
            "To calculate it, I need the following values:\n"
            "1. Principal (initial investment)\n"
            "2. Rate (annual interest rate as a percentage)\n"
            "3. Time (number of years)\n"
            "4. Times compounded per year (how often interest is added)"
        )
    else:
        # Use AI to generate a more dynamic response
        response = model.generate_content(user_message)
        response_text = response.text
    
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True)
try:
    response = model.generate_content(user_message)
except google.api_core.exceptions.NotFound as e:
    print("Error: The specified model was not found. Please check the model name or API version.")
    response_text = "Sorry, there was an error processing your request. Please try again later."
