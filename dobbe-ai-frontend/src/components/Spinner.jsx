// Spinner.jsx
import React from 'react';
import './Spinner.css';

const Spinner = () => {
  return (
    <div className="spinner-overlay">
      <div className="spinner" />
      <p className="loading-text">Analyzing DICOM... Please wait</p>
    </div>
  );
};

export default Spinner;
