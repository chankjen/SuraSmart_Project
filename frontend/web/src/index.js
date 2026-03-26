import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/global.css';
import App from './App';

// MetaMask Error Guard: Suppress external extension errors that block development
const isMetaMaskError = (error) => {
  const message = error?.message || '';
  const stack = error?.stack || '';
  const reason = error?.reason?.message || '';
  return (
    message.includes('MetaMask') || 
    message.includes('eth_requestAccounts') ||
    stack.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    reason.includes('MetaMask')
  );
};

window.addEventListener('error', (event) => {
  if (isMetaMaskError(event)) {
    event.stopImmediatePropagation();
    console.debug('[MetaMask Guard] Suppressed error:', event.message);
  }
});

window.addEventListener('unhandledrejection', (event) => {
  if (isMetaMaskError(event.reason)) {
    event.stopImmediatePropagation();
    event.preventDefault();
    console.debug('[MetaMask Guard] Suppressed promise rejection:', event.reason?.message);
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
