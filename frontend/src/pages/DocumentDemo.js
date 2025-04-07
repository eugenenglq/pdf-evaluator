import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket from '../common/useWebSocket';
import {
  Container,
  Header,
  SpaceBetween,
  Grid,
  FormField,
  Textarea,
  Button,
  Alert,
  FileUpload,
  Select,
  Input
} from "@cloudscape-design/components";

function DocumentDemo() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [promptTitle, setPromptTitle] = useState('');
  const [savedPrompts, setSavedPrompts] = useState([]);
  const [selectedPromptOption, setSelectedPromptOption] = useState(null);
  const [domainName, setDomainName] = useState(null);
  const API_ENDPOINT = process.env.REACT_APP_API_ENDPOINT;
  const API_STAGE = process.env.REACT_APP_APIGATEWAY_STAGE

  const handleWebSocketMessage = useCallback((data) => {
    console.log(data);
    if (data.chunk) {
      setResult(prevResult => prevResult ? prevResult + data.chunk : data.chunk);
    }
    if (data.done === true) {
      setIsLoading(false);
      setSuccess('Evaluation completed successfully!');
    }
    if (data.error) {
      setIsLoading(false);
    }
  }, []); 
  
  const { 
    connectionId
  } = useWebSocket(handleWebSocketMessage);

  useEffect(() => {
    // Load saved prompts
    loadSavedPrompts();
    setDomainName(`${process.env.REACT_APP_WS_ENDPOINT}`);

    // Cleanup function to disconnect WebSocket when component unmounts
    return () => {
      // if (wsClient) {
      //   wsClient.disconnect();
      // }
    };
  }, []);

  const loadSavedPrompts = async () => {
    try {
      const response = await fetch(`${API_ENDPOINT}/manage-prompts?demo=srb`);
      const data = await response.json();
      setSavedPrompts(data);
    } catch (error) {
      console.error('Error loading prompts:', error);
      setError('Failed to load saved prompts');
    }
  };

  const handleFileChange = ({ detail }) => {
    if (detail.value.length > 0) {
      setFile(detail.value[0]);
      setError('');
    } else {
      setFile(null);
    }
  };

  const handlePromptChange = (event) => {
    setPrompt(event.detail.value);
  };

  const handlePromptTitleChange = (event) => {
    setPromptTitle(event.detail.value);
  };

  const handleSavePrompt = async () => {
    if (!prompt || !promptTitle) {
      setError('Please enter both prompt title and prompt text');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      setSuccess('');

      const response = await fetch(`${API_ENDPOINT}/manage-prompts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          demo: 'srb',
          title: promptTitle,
          prompt: prompt,
        }),
      });

      if (response.ok) {
        setSuccess('Prompt saved successfully!');
        await loadSavedPrompts();
      } else {
        throw new Error('Failed to save prompt');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      setError('Failed to save prompt');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluate = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setResult('');

    try {
      // Prepare the payload
      const payload = {
        action: 'processImage', // Add action field for server routing
        connectionId: connectionId,
        stage: API_STAGE,
        domainName: domainName,
        file: file ? await fileToBase64(file) : null,
        prompt: prompt,
        type: 'evaluation' // Add a type to distinguish this from other websocket messages
      };

      const response = await fetch(`${API_ENDPOINT}/start-process-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'omit',
        body: JSON.stringify(payload)
      });

      // Log the full response
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      setResult(data.response);
      setSuccess('Evaluation completed successfully!');
      setIsLoading(false);

    } catch (err) {
      setError('An error occurred during evaluation. Please try again.');
      console.error(err);
      setIsLoading(false);
    }
  };

  // Helper function to convert File to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const clearAll = () => {
    setFile(null);
    setPrompt('');
    setResult('');
    setError('');
    setSuccess('');
  };

  return (
    <Container>
      <Grid
        gridDefinition={[{ colspan: 4 }, { colspan: 8 }]}
      >
        <div>
          <SpaceBetween size="m">
            <Header variant="h1">
              PDF Evaluator
              {/* <WebSocketStatus 
              isConnected={isWebSocketConnected} 
              hasConnectionDetails={connectionId !== null && domainName !== null} 
            /> */}
            </Header>

            {error && (
              <Alert type="error">
                {error}
              </Alert>
            )}

            {success && (
              <Alert type="success">
                {success}
              </Alert>
            )}

            <FormField label="Saved Prompts">
              <Select
                selectedOption={selectedPromptOption}
                onChange={({ detail }) => {
                  setSelectedPromptOption(detail.selectedOption);
                  if (detail.selectedOption) {
                    const promptData = savedPrompts.find(p => p.title === detail.selectedOption.value);
                    if (promptData) {
                      setPrompt(promptData.prompt);
                      setPromptTitle(promptData.title);
                    }
                  }
                }}
                options={savedPrompts.map(p => ({
                  value: p.title,
                  label: p.title
                }))}
                placeholder="Select a saved prompt"
              />
            </FormField>

            <FormField label="Prompt Title">
              <Input
                value={promptTitle}
                onChange={handlePromptTitleChange}
                placeholder="Enter title to save this prompt"
              />
            </FormField>

            <FormField label="Prompt">
              <Textarea
                value={prompt}
                onChange={handlePromptChange}
              />
            </FormField>


            <Button
              variant="primary"
              onClick={handleSavePrompt}
              loading={isLoading}
              disabled={!prompt || !promptTitle}
            >
              Save Prompt
            </Button>

            <FormField label="PDF Upload">
              <FileUpload
                onChange={handleFileChange}
                value={file ? [file] : []}
                constraintText="Only PDF files are supported"
                accept="application/pdf"
                multiple={false}
                showFileSize
                showFileLastModified
                i18nStrings={{
                  uploadButtonText: e =>
                    e ? "Choose different file" : "Choose file",
                  dropzoneText: e =>
                    e ? "Drop file to replace" : "Drop file",
                  removeFileAriaLabel: e =>
                    `Remove file ${e.name}`
                }}
              />
            </FormField>

            <Button
              variant="primary"
              onClick={handleEvaluate}
              loading={isLoading}
              disabled={!file || !prompt}
            >
              Evaluate
            </Button>
          </SpaceBetween>
        </div>
        <div>
          {result && (
            <Container
              header={
                <Header variant="h2">
                  Evaluation Result
                </Header>
              }
            >
              <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#f8f8f8', padding: '10px', borderRadius: '4px' }}>
                {result}
              </pre>
            </Container>
          )}
        </div>
      </Grid>
    </Container>
  );
}

export default DocumentDemo;