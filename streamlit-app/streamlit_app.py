import streamlit as st
import boto3
import base64
import os

# Initialize session state for prompts
if 'prompts' not in st.session_state:
    st.session_state.prompts = []
if 'selected_prompt' not in st.session_state:
    st.session_state.selected_prompt = None
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'editing' not in st.session_state:
    st.session_state.editing = False
if 'edited_prompt' not in st.session_state:
    st.session_state.edited_prompt = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "anthropic.claude-3-5-sonnet-20240620-v1:0"


# Add model options
BEDROCK_MODELS = {
    "Claude 3.5 Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0"
}


def initialize_bedrock_client():
    region = os.getenv('BEDROCK_REGION', 'ap-southeast-1')
    bedrock_runtime = boto3.client('bedrock-runtime', region)
    return bedrock_runtime

def initialize_dynamodb():
    """Initialize DynamoDB client"""
    dynamodb = boto3.resource('dynamodb')
    return dynamodb

def handle_form_submission():
    if st.session_state.new_title and st.session_state.new_prompt:
        if save_prompt(st.session_state.new_title, st.session_state.new_prompt):
            st.session_state.form_submitted = True
            st.rerun()

def load_prompts():
    """Load prompts directly from DynamoDB"""
    try:
        dynamodb = initialize_dynamodb()
        table = dynamodb.Table('tr-agent-prompts')
        
        response = table.scan()
        
        prompts = response.get('Items', [])
        st.session_state.prompts = prompts
        return prompts
    except Exception as e:
        st.error(f"Error loading prompts: {str(e)}")
        return []

def save_prompt(title, prompt_text, is_update=False):
    """Save a new prompt or update existing prompt in DynamoDB"""
    try:
        print('save_prompt1')
        # Check if title already exists (for new prompts)
        if not is_update:
            print('save_prompt2')
            existing_prompt = next((p for p in st.session_state.prompts if p['title'] == title), None)
            if existing_prompt:
                st.error(f"A prompt with title '{title}' already exists. Please choose a different title.")
                return False

        dynamodb = initialize_dynamodb()
        table = dynamodb.Table('tr-agent-prompts')
        
        item = {
            'title': title,
            'prompt': prompt_text
        }
        
        table.put_item(Item=item)
        st.success("Prompt {} successfully!".format("updated" if is_update else "saved"))
        
        # Reload prompts and update session state
        st.session_state.prompts = load_prompts()
        
        # Clear input fields after successful save using the callback
        if not is_update:
            clear_form()
        
        return True
        
        return True
    except Exception as e:
        st.error(f"Error {'updating' if is_update else 'saving'} prompt: {str(e)}")
        return False

def clear_form():
    st.session_state['new_title'] = ''
    st.session_state['new_prompt'] = ''

def process_pdf_with_bedrock(pdf_content, bedrock_client):
    modelID = st.session_state.selected_model
    print('modelID', modelID)

    # Initialize the placeholder for streaming output
    output_placeholder = st.empty()
    
    # Encode PDF content to base64
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    # Use the selected prompt or default prompt
    prompt = st.session_state.selected_prompt['prompt'] if st.session_state.selected_prompt else """Please analyze and summarize the content of this PDF document. 
    Focus on the main points and key findings. Provide a clear and concise summary."""
    
    doc_message = {
            "role": "user",
            "content": [
                {
                    "document": {
                        "name": "Document 1",
                        "format": "pdf",
                        "source": {
                            "bytes": pdf_content
                        }
                    }
                },
                { "text": "Based on the document, " + prompt }
            ]
        }
    
    try:
        response_stream = bedrock_client.converse_stream(
                modelId=modelID,
                messages=[doc_message],
                inferenceConfig={
                    "maxTokens": 2000,
                    "temperature": 0
                },
            )
            
        # For WebSocket requests, send each chunk as it arrives
        full_response = ""

        for chunk in response_stream["stream"]:
            if "contentBlockDelta" in chunk:
                text_chunk = chunk["contentBlockDelta"]["delta"]["text"]
                full_response += text_chunk
                output_placeholder.markdown(full_response)
                    
        return full_response
    
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def handle_save_changes():
    # Get the edited prompt from session state
    edited_prompt = st.session_state.edited_prompt
    
    # Validate that we have both a selected prompt and an edited prompt
    if not st.session_state.selected_prompt:
        st.error("No prompt selected for editing")
        return
        
    if not edited_prompt or edited_prompt.strip() == "":
        return
        
    # Save the changes
    if save_prompt(st.session_state.selected_prompt['title'], 
                  edited_prompt.strip(), 
                  is_update=True):
        st.session_state.editing = False
        st.session_state.form_submitted = True

          
def toggle_edit_mode():
    """Enable editing mode and initialize the edited_prompt with the current prompt value"""
    if st.session_state.selected_prompt:
        st.session_state.editing = True
        # Always initialize with the current prompt to avoid None/empty values
        print('st.session_state.edited_prompt =', st.session_state.selected_prompt['prompt'])
        st.session_state.edited_prompt = st.session_state.selected_prompt['prompt']
    else:
        st.error("Please select a prompt to edit")


def handle_cancel():
    """Cancel editing and reset to initial state"""
    st.session_state.editing = False
    # Reset edited_prompt to the original prompt value instead of None
    if st.session_state.selected_prompt:
        st.session_state.edited_prompt = st.session_state.selected_prompt['prompt']


def main():
    st.title("PDF Evaluator")
    
    # Initialize session states
    if 'editing' not in st.session_state:
        st.session_state.editing = False
    if 'new_title' not in st.session_state:
        st.session_state.new_title = ""
    if 'new_prompt' not in st.session_state:
        st.session_state.new_prompt = ""
    
    # Initialize Bedrock client
    bedrock_client = initialize_bedrock_client()
    
    # Load prompts when the app starts
    if len(st.session_state.prompts) == 0:
        load_prompts()
    
    # Move prompt management to sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Add model selector
        selected_model_name = st.selectbox(
            "Select Bedrock Model",
            options=list(BEDROCK_MODELS.keys()),
            index=list(BEDROCK_MODELS.values()).index(st.session_state.selected_model)
        )
        
        st.session_state.selected_model = BEDROCK_MODELS[selected_model_name]
        
        st.markdown("---")

        st.header("Prompt Management")
        
        # Prompt selection dropdown
        prompt_titles = [p['title'] for p in st.session_state.prompts]
        if prompt_titles:
            selected_title = st.selectbox(
                "Select a prompt",
                prompt_titles,
                key="prompt_selector"
            )
            selected_prompt = next((p for p in st.session_state.prompts if p['title'] == selected_title), None)
            st.session_state.selected_prompt = selected_prompt
            
            if selected_prompt:
                if st.session_state.editing:
                    # Ensure we have a valid initial value
                    if st.session_state.edited_prompt is None:
                        st.session_state.edited_prompt = selected_prompt['prompt']
                    edited_prompt = st.text_area(
                        "Edit Prompt",
                        value=st.session_state.edited_prompt,
                        height=100,
                        key="edited_prompt",
                        help="Enter your prompt text here. This field cannot be empty."
                    )
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.button("Save Changes", 
                                on_click=handle_save_changes,
                                key="save_changes")
                    with col2:
                        st.button("Cancel", 
                                on_click=handle_cancel,
                                key="cancel_edit")
                else:
                    st.text_area("Current Prompt", 
                                selected_prompt['prompt'], 
                                height=100, 
                                disabled=True)
                    st.button("Edit Prompt", 
                            on_click=toggle_edit_mode,
                            key="edit_button")
        
            if st.session_state.form_submitted:
                st.session_state.prompts = load_prompts()
                st.session_state.form_submitted = False
        else:
            st.info("No prompts available. Create a new prompt below.")
        
        st.markdown("---")

        # New prompt creation
        st.subheader("Create New Prompt")
        with st.form(key='prompt_form'):
            new_title = st.text_input("Prompt Title", key="new_title")
            new_prompt = st.text_area("Prompt Text", height=100, key="new_prompt")
            submit_button = st.form_submit_button("Save Prompt", on_click=handle_form_submission)
        
            if submit_button and (not new_title or not new_prompt):
                if new_title and new_prompt:
                    if save_prompt(new_title, new_prompt):
                        st.rerun()  # Force a rerun to update the dropdown
                else:
                    st.warning("Please fill in both title and prompt text")
    
    
    # Display selected prompt info in main area
    if st.session_state.selected_prompt:
        st.info(f"Selected Prompt: {st.session_state.selected_prompt['title']}")
        with st.expander("View Selected Prompt"):
            st.write(st.session_state.selected_prompt['prompt'])
    else:
        st.warning("Please select a prompt from the sidebar before processing a PDF")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Show file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write(file_details)
        
        # Process button
        if st.button("Process PDF"):
            if not st.session_state.selected_prompt:
                st.warning("Please select a prompt before processing")
            else:
                with st.spinner("Processing PDF..."):
                    # Read PDF content
                    pdf_content = uploaded_file.read()
                    
                    # Process PDF with Bedrock
                    summary = process_pdf_with_bedrock(pdf_content, bedrock_client)
                    
                    # if summary:
                    #     st.success("PDF processed successfully!")
                    #     st.subheader("Summary")
                    #     st.write(summary)

if __name__ == "__main__":
    main()













