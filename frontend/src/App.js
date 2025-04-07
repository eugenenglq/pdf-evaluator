import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import {
  AppLayout,
  SideNavigation
} from "@cloudscape-design/components";
import "@cloudscape-design/global-styles/index.css";

// Import pages
import Home from './pages/Home';
import DocumentDemo from './pages/DocumentDemo';

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeHref, setActiveHref] = useState(location.pathname);
  
  const handleNavigate = (e) => {
    setActiveHref(e.detail.href);
    navigate(e.detail.href);
  };
  
  // Navigation items for sidebar
  const navItems = [
    {
      type: 'link',
      text: 'Home',
      href: '/'
    },
    {
      type: 'link',
      text: 'Document Demo',
      href: '/document-demo'
    }
  ];
  
  return (
    <AppLayout
      navigation={
        <SideNavigation
          activeHref={activeHref}
          header={{ text: 'Demo Platform', href: '/' }}
          items={navItems}
          onFollow={handleNavigate}
        />
      }
      content={
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/document-demo" element={<DocumentDemo />} />
        </Routes>
      }
      toolsHide={true}
      contentType="default"
    />
  );
}
export default App;