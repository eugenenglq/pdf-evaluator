// Component for collapsible panel
const CollapsiblePanel = ({ title, isOpen = true, onToggle, children }) => {
  return (
    <div className="collapsible-panel">
      <div className="collapsible-header" onClick={onToggle}>
        <span>{title}</span>
        <span>{isOpen ? '▲' : '▼'}</span>
      </div>
      {isOpen && (
        <div className="collapsible-content">
          {children}
        </div>
      )}
    </div>
  );
};

// Component for file upload
const FileUpload = ({ onFileSelected }) => {
  const [file, setFile] = React.useState(null);
  const fileInputRef = React.useRef(null);

  const handleFileDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelection(droppedFile);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setFile(selectedFile);
    onFileSelected(selectedFile);
  };

  const handleFileInputChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      handleFileSelection(selectedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleAreaClick = () => {
    fileInputRef.current.click();
  };

  const handleRemoveFile = () => {
    setFile(null);
    onFileSelected(null);
    fileInputRef.current.value = '';
  };

  return (
    <div>
      {!file ? (
        <div
          className="file-upload-area"
          onDrop={handleFileDrop}
          onDragOver={handleDragOver}
          onClick={handleAreaClick}
        >
          <p>Drag & drop a file here, or click to select a file</p>
          <input
            type="file"
            ref={fileInputRef}
            className="file-upload-input"
            onChange={handleFileInputChange}
          />
        </div>
      ) : (
        <div className="file-info">
          <span className="file-name">{file.name}</span>
          <button className="btn btn-secondary" onClick={handleRemoveFile}>Remove</button>
        </div>
      )}
    </div>
  );
};

// Main App Component
const App = () => {
  const [file, setFile] = React.useState(null);
  const [prompt, setPrompt] = React.useState('');
  const [result, setResult] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isPromptOpen, setIsPromptOpen] = React.useState(true);
  const [error, setError] = React.useState('');
  const [success, setSuccess] = React.useState('');

  const handleFileSelected = (selectedFile) => {
    setFile(selectedFile);
    setError('');
  };

  const handlePromptChange = (event) => {
    setPrompt(event.target.value);
    setError('');
  };

  const handleSubmit = async () => {
    // Validation
    if (!file && !prompt.trim()) {
      setError('Please upload a file or provide a prompt.');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Simulate API call with a timeout
      await new Promise(resolve => setTimeout(resolve, 2000));

      // This is where you would normally handle the actual API call
      // const formData = new FormData();
      // if (file) formData.append('file', file);
      // if (prompt) formData.append('prompt', prompt);
      // const response = await fetch('your-api-endpoint', {
      //   method: 'POST',
      //   body: formData
      // });
      // const data = await response.json();
      // setResult(data.result);

      // For demo, set a sample result
      setResult(`Processing complete.\nFile: ${file ? file.name : 'None'}\nPrompt: ${prompt || 'None'}`);
      setSuccess('Request processed successfully!');
    } catch (err) {
      setError('An error occurred while processing your request. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPrompt('');
    setResult('');
    setError('');
    setSuccess('');
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">File Analysis Tool</h1>
      </header>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Upload File</h2>
        </div>
        <FileUpload onFileSelected={handleFileSelected} />
      </div>
      
      <CollapsiblePanel 
        title="Prompt (Optional)" 
        isOpen={isPromptOpen} 
        onToggle={() => setIsPromptOpen(!isPromptOpen)}
      >
        <textarea
          className="textarea-field"
          value={prompt}
          onChange={handlePromptChange}
          placeholder="Enter additional instructions or context here..."
        ></textarea>
      </CollapsiblePanel>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Results</h2>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        {isLoading ? (
          <div className="result-loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="results-panel">
            {result || 'Results will appear here after submitting your request.'}
          </div>
        )}
        
        <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
          <button className="btn" onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Submit'}
          </button>
          <button className="btn btn-secondary" onClick={handleReset}>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};

// Render the App
ReactDOM.render(<App />, document.getElementById('root'));