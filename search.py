import streamlit as st
import fitz
import pandas as pd
import os
from pdf2image import convert_from_path
import pytesseract
import re

def search_word_in_text(word, text):
    word = word.lower()  # Convert the search word to lowercase
    text = text.lower()  # Convert the text to lowercase
    if word in text:
        return True
    else:
        return False

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

text = ""

@st.cache_data
def ReadText(uploaded_file, isOCR):
    text = ""
    print(1)
    with open('uploads/' + uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    f.close()

    file = os.path.join("uploads", uploaded_file.name)

    if isOCR:
        pages = convert_from_path(file, poppler_path=r'D:\Yukio\poppler-23.11.0\Library\bin')
        for page in pages:
            page_text = pytesseract.image_to_string(page)
            text += page_text
        
        sentences = text.split('\n\n')

    else:
        with fitz.open(file) as doc:
            for page in doc:
                text += page.get_text()

        sentences = text.split(')\n')

    return sentences

isOCR = st.toggle('Active OCR')

if isOCR:
    st.write('OCR is Active!')

if uploaded_file:
    sentences = ReadText(uploaded_file, isOCR)

    input_value1 = ""
    input_value2 = ""
    input_value3 = ""
    input_value4 = ""
    input_value5 = ""
    input_value6 = ""

    col1, col2, col3 = st.columns(3)

    with col1:
        show_input1 = st.checkbox('Numero do Processo', key=1)
        show_input2 = st.checkbox('Natureza/Tipo/Classe', key=2)

    with col2:
        show_input3 = st.checkbox('Autor/Requerente', key=3)
        show_input4 = st.checkbox('Reu/Requerido', key=4)

    with col3:
        show_input5 = st.checkbox('Andamento', key=5)
        show_input6 = st.checkbox('Advogados', key=6)

    if show_input1:
        input_value1 = st.text_input('Numero do Processo', key=7)

    if show_input2:
        input_value2 = st.text_input('Natureza /Tipo/ Classe', key=8)

    if show_input3:
        input_value3 = st.text_input('Autor/Requerente', key=9)

    if show_input4:
        input_value4 = st.text_input('Reu/Requerido', key=10)

    if show_input5:
        input_value5 = st.text_input('Andamento', key=11)

    if show_input6:
        input_value6 = st.text_input('Advogados', key=12)

    col4, col5, col6 = st.columns(3)
    with col4:
        button = st.button('search')
    if button:
        keys = [input_value1, input_value2, input_value3, input_value4, input_value5, input_value6]

        resultText = []

        for sentence in sentences:
            s = sentence.replace('\n', '')
            isOk = True
            
            for key in keys:
                if key == "":
                    continue
                if search_word_in_text(key, s):
                    isOk = False
                    break
            
            if isOk and s.find(" - ADV") > 0 and s.find("Processo") == 0:
                if isOCR:
                    resultText.append(s)
                else:
                    resultText.append(s + ')')

        with col5:
            st.write("Search Results: ", len(resultText))

        if len(resultText):
            numero = []
            classe = []
            author = []
            adv = []
            reu = []
            andamento = []
            for result in resultText:
                numero.append(result[result.find("Processo"):result.find(" - ")])
                adv.append(result[result.find(" - ADV")+3:])
                result = result[result.find(" - ")+3:result.find(" - ADV")]
                cla = result[:result.find(" - ")+3]
                result = result[result.find(" - ")+3:]
                classe.append(cla + result[:result.find(" - ")])
                result = result[result.find(" - ")+3:]
                author.append(result[:result.find(" - ")])
                result = result[result.find(" - ")+3:]
                andamento.append(result[result.rfind(" - ")+3:])
                reu.append(result[:result.rfind(" - ")])
            data = {
                    'Numero do Processo': numero, 
                    'Natureza /Tipo/ Classe': classe, 
                    'Autor/Requerente': author, 
                    'Reu/Requerido': reu, 
                    'Andamento': andamento,
                    'Advogados': adv
                }
            df = pd.DataFrame(data)

            df.to_excel("output.xlsx", index=False)

            with open("./output.xlsx", "rb") as file:
                file_contents = file.read()
                with col6:
                    download_button = st.download_button("Download", file_contents, file_name="output.xlsx")
