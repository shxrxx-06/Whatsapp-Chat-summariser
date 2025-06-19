import google.generativeai as genai

API_KEY = "AIzaSyBiFtppOR5vsvCqPI1a8jRcT-82Q3O-j94"
genai.configure(api_key=API_KEY)

def get_gemini_response(chat_history):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = """
    You are a helpful assistant designed to summarize WhatsApp chat conversations for police officers.
    Your task is to extract the following information from the provided chat history:
    1. A concise summary of the main topics discussed.
    2. A list of actionable tasks, including who is responsible and the deadline if mentioned.
    3. A list of important keywords or phrases that might be relevant for investigation.

    The output should be structured as follows:

    Summary of Topics:
    [Concise summary of topics]

    Actionable Tasks:
    - Task: [Task description], Responsible: [Person], Deadline: [Date/Time or N/A]
    - Task: [Task description], Responsible: [Person], Deadline: [Date/Time or N/A]

    Flagged Keywords:
    - [Keyword 1]
    - [Keyword 2]

    Raw Gemini Output:
    [Raw output from Gemini, if needed for fallback]

    Chat History:
    """
    full_prompt = prompt + chat_history
    response = model.generate_content(full_prompt)
    return response.text

if __name__ == '__main__':
    from whatsapp_parser import parse_whatsapp_chat
    df = parse_whatsapp_chat('test_chat.txt')
    chat_history = df.to_string()
    response = get_gemini_response(chat_history)
    print(response)


