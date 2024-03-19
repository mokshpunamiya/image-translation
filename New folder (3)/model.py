import os
import fitz
from fpdf import FPDF
import pytesseract
from PIL import Image
from openai import OpenAI

OPENAI_API_KEY = "PUT_OPEN_API_KEY_HERE"
client = OpenAI(api_key=OPENAI_API_KEY)

def translate_gujarati_to_english(text):
    translated_text = chat_with_openai(text)
    return translated_text

def chat_with_openai(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Translate Gujarati text extracted from images to English. If corrections or clarifications are needed for accuracy just do it, and provide the revised text with appropriate formatting. Provide English output only." + prompt}
        ]
    )
    return completion.choices[0].message.content

def extract_text_and_translate(input_pdf_path, pdf_name):
    try:
        custom_config = r'--oem 1 --psm 3 -l guj'
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        doc = fitz.open(input_pdf_path)
        for i, page in enumerate(doc):
            image_path = "temp_image.png"
            pix = page.get_pixmap()
            pix.save(image_path)
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config=custom_config)
            translated_text = translate_gujarati_to_english(text)
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Page {i+1}:", ln=True, align='L')
            pdf.multi_cell(0, 10, txt=translated_text)
            os.remove(image_path)
        
        doc.close()

        os.remove(f"raw_files/{pdf_name}")
        pdf.output(f"output_files/{pdf_name}")

        return 'success'
    except:
        return 'failed'
