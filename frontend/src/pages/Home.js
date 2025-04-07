import React from 'react';
import {
  Container,
  Header,
  Box,
  SpaceBetween,
} from "@cloudscape-design/components";

function Home() {
  return (
    <Container>
      <SpaceBetween size="l">
        <Header variant="h1">Welcome to the Demo Platform</Header>
        <Box>
          <p>This platform hosts various demos. Please use the navigation sidebar to explore available demos.</p>
          <p>Currently available demos:</p>
          <ul>
            <li>Document Analyzer - Upload your PDF file and analyze using Generative AI.</li>
          </ul>
        </Box>
      </SpaceBetween>
    </Container>
  );
}

export default Home;