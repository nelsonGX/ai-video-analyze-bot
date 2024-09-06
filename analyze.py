from load_config import gemini_api_key
import google.generativeai as genai

genai.configure(api_key=gemini_api_key)

def upload_to_gemini(path):
    file = genai.upload_file(path)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="You are a video analyzer, you have to watch the video user provided, and respond with detailed description of the video. User may ask follow-up questions. User is using language zh-tw.",
    safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "block_none"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "block_none"
        }
    ]
)

async def generate_analyze(file):
    global convo
    convo = model.start_chat()
    is_finished = False

    while not is_finished:
        try:
            reply_msg = await convo.send_message_async(
                [file]
            )
            is_finished = True
        except Exception as e:
            print(f"Error: {e}")
            print("retrying...")

    return reply_msg.text + "\n\n" + "-# Reply to this message to ask follow-up questions."

async def ask_followup(question):
    global convo
    reply_msg = await convo.send_message_async(
        question
    )
    return reply_msg.text