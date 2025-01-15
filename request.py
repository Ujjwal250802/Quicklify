import requests
import json
import gradio as gr
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}
history = []  

def generate_response(prompt):
    """
    Generate a response based on the given prompt using the external API.
    """
    global history
    history.append(prompt)
    final_prompt = "\n".join(history)

    data = {
        "model": "Quicklify",
        "prompt": final_prompt,
        "stream": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response = response.text
        data = json.loads(response)
        actual_response = data['response']
        return actual_response
    else:
        print("Error:", response.text)
        return "Error occurred while generating response."

def extract_text_from_scanned(pdf_file):
    """
    Extract text from a scanned PDF using OCR (Tesseract).
    """
    images = convert_from_path(pdf_file.name)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

def summarize_pdf(pdf_file):
    """
    Summarize the content of a PDF file.
    """
    try:
        # Step 1: Extract text
        reader = PdfReader(pdf_file.name)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()

        # Step 2: Handle cases with no text (e.g., scanned PDFs)
        if not pdf_text.strip():
            pdf_text = extract_text_from_scanned(pdf_file)

        # Step 3: Summarize extracted text
        if pdf_text.strip():
            summary = generate_response("Summarize the following content:\n" + pdf_text)
            return f"Text Summary:\n{summary}"
        else:
            return "The uploaded PDF is empty or could not be read."
    except Exception as e:
        return f"An error occurred while processing the PDF: {str(e)}"

def process_input(prompt, pdf_file):
    """
    Process user input (either a prompt or a PDF) and reset history for new sessions.
    """
    global history
    if pdf_file:
        history = [] 
        return summarize_pdf(pdf_file)
    elif prompt:
        history = [] 
        return generate_response(prompt)
    else:
        return "Please provide either a prompt or a PDF file."

interface = gr.Interface(
    fn=process_input,
    inputs=[
        gr.Textbox(lines=2, placeholder='Enter your prompt'),
        gr.File(label="Upload a PDF", file_types=[".pdf"])
    ],
    outputs="text",
    live=False
)
interface.launch()