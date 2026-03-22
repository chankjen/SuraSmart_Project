import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/global.css';
import App from './App';

// MetaMask Error Guard: Suppress external extension errors that block development
window.addEventListener('error', (event) => {
  if (event.message?.includes('MetaMask') || 
      event.filename?.includes('chrome-extension://') ||
      event.error?.stack?.includes('MetaMask')) {
    event.stopImmediatePropagation();
    console.warn('[MetaMask Guard] Suppressed external extension error:', event.message);
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
