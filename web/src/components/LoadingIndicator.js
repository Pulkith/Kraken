import React from 'react';
import '../styles/LoadingIndicator.css';

function LoadingIndicator({ status }) {
  return (
    <div className="loading-container">
      <div className="loading-animation">
        <div className="spinner"></div>
        <div className="pulse"></div>
      </div>
      <div className="loading-status">{status}</div>
    </div>
  );
}

export default LoadingIndicator;
