import google.generativeai as genai

API_KEY = "AIzaSyCgqWIHw2eQF5CWSd-6qCcA-DHsI6xl2q0"
genai.configure(api_key=API_KEY)

for m in genai.list_models():
    print(m.name)


