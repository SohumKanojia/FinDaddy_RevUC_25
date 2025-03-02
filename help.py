from google import genai
client = genai.Client(api_key="AIzaSyBXalr25Xvh2LQbzbUEwvIEfA2hvUNbosA")
while(True):
    query = input("Enter your query: ")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents = query
    )
    print(response.text)