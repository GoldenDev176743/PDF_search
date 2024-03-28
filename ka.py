import streamlit as st
import csv
import openai
import concurrent.futures
import time
import random
import string
import os


def get_ai_response(prompt: str) -> str:
    model = "gpt-3.5-turbo"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150  # Adjust as needed
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error during API call: {e}")
        return ""

def process_csv_row(row, executor, delay_after=25, delay_duration=10):
    """
    Processes a CSV row, replacing the [prompt] placeholder with the actual product description
    and generating content using the OpenAI API.
    """
    processed_row = {}
    processed_row['describe_product'] = row['describe_product']
    tasks = ['keywords', 'short_description', 'long_description', 'title']

    for task in tasks:
        if '[prompt]' in row[task]:
            # Replace the placeholder with the actual product description
            prompt = row[task].replace('[prompt]', row['describe_product'])
            # Use the executor to run the API call in a separate thread
            future = executor.submit(get_ai_response, prompt)
            processed_row[task] = future.result()
        else:
            processed_row[task] = row[task]

    return processed_row

@st.cache_data
def process_input_csv_file(input_file_name: str, delay_after=25, delay_duration=10):
    with open(input_file_name, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    processed_rows = []
    row_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for row in rows:
            row_count += 1
            processed_row = process_csv_row(row, executor, delay_after, delay_duration)
            processed_rows.append(processed_row)

            # Introduce a delay after processing every 'delay_after' number of rows
            if row_count % delay_after == 0:
                time.sleep(delay_duration)

    return processed_rows

def generate_random_code(length=5):
    """Generate a random alphanumeric code of given length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

# CSV processing
def process_and_download_csv(uploaded_file):
    if uploaded_file is not None:
        with open('./' + uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.read())
        f.close()

        # output = os.path.join("uploads", uploaded_file.name)
        output = process_input_csv_file(os.path.join("./", uploaded_file.name))
        
        # Generate a unique filename with timestamp and random code
        timestamp = time.strftime("%Y%m%d%H%M%S")
        random_code = generate_random_code()
        unique_filename = f"processed_output_{timestamp}_{random_code}.csv"

        # Allow users to download the processed data as CSV with a unique filename
        with open(unique_filename, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output[0].keys())
            writer.writeheader()
            writer.writerows(output)
        with open(unique_filename, 'rb') as file:
            st.download_button(
                label="Download CSV",
                data=file,
                file_name=unique_filename,
                mime='text/csv'
            )

def display_tutorial():
    st.markdown("""
    ## Welcome to the Bulk CSV to GPT Processing tool! 🚀

    This tool enables you to generate descriptions for multiple products in a CSV file using OpenAI's GPT-3.5 model.
    """)

    st.markdown("""
    ### Example Prompts Explanation

    - **describe_product**: This column should contain the name of the product.
    - **keywords**: Generate up to 5 keywords for the product description. Separate them by comma only. The [prompt] placeholder grabs the product description, so you can add whatever uniqueness you want.
    - **short_description**: Write a short description for the product emphasizing comfort, usability, and material quality, with a maximum of 50 words.
    - **long_description**: Provide a detailed description for the product highlighting its unique features, fabric quality, and care instructions, with a minimum of 150 words.
    - **title**: Create an e-commerce product title for the product that is catchy, mentions key features, and is without quotes. The [prompt] placeholder will be replaced with the product description.
    """)

# Streamlit UI
st.title("Bulk CSV to GPT Processing")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    st.write("Processing the file...")

    # Process CSV and download the processed CSV
    process_and_download_csv(uploaded_file)

# Display tutorial
display_tutorial()
