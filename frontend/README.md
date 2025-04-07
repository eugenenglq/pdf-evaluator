# File Upload and Analysis Application

This is a React.js application with a professional Salesforce-like UI that allows users to upload files, provide additional context via a collapsible textbox, and view results after processing.

## Features

- **File Upload**: Drag and drop functionality or traditional file selection
- **Collapsible Prompt Box**: Expandable/collapsible text area for additional instructions
- **Results Display**: Clean display area for API responses
- **Professional UI**: Salesforce-inspired design system
- **Loading States**: Visual feedback during processing

## Getting Started

1. Simply open the `index.html` file in a web browser.
2. The application uses CDN-hosted React, ReactDOM, and Babel for simplicity.

## Integration with Backend

To connect this frontend to a real API:

1. Uncomment and modify the API call section in the `handleSubmit` function in `app.js`
2. Update the API endpoint URL and adjust the request format as needed
3. Process the API response accordingly

## Technologies Used

- React.js
- CSS3 with custom variables
- Drag and drop API