# import streamlit as st
# import boto3
# from botocore.config import Config
# import json
# import time
# import base64
# from PyPDF2 import PdfReader
# import io

# # Initialize AWS Bedrock client
# bedrock = boto3.client(
#     service_name='bedrock-runtime',
#     config=Config(
#         region_name='us-east-1'  # Replace with your region
#     )
# )

# def process_pdf(pdf_file, prompt):
#     # Read PDF content
#     pdf_reader = PdfReader(pdf_file)
#     text_content = ""
#     for page in pdf_reader.pages:
#         text_content += page.extract_text()

#     # Prepare prompt for Bedrock
#     message = f"{prompt}\n\nDocument content:\n{text_content}"
    
#     # Prepare request for Claude model
#     body = json.dumps({
#         "prompt": f"\n\nHuman: {message}\n\nAssistant:",
#         "max_tokens_to_sample": 4096,
#         "temperature": 0.5,
#         "top_k": 250,
#         "top_p": 1,
#         "stop_sequences": ["\n\nHuman:"]
#     })

#     # Invoke Bedrock
#     response = bedrock.invoke_model(
#         modelId="anthropic.claude-v2",  # Replace with your preferred model
#         body=body
#     )
    
#     response_body = json.loads(response.get('body').read())
#     return response_body.get('completion', '').strip()

# # Streamlit UI
# st.title('PDF Summarizer with AWS Bedrock')

# # File upload
# uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])

# # Text input for prompt
# prompt = st.text_area(
#     "Enter your prompt",
#     value="Please summarize this document.",
#     height=100
# )

# if uploaded_file and st.button('Process PDF'):
#     with st.spinner('Processing PDF...'):
#         try:
#             # Process the PDF and get response
#             response = process_pdf(uploaded_file, prompt)
            
#             # Display results
#             st.subheader("Summary Results")
#             st.write(response)
            
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")