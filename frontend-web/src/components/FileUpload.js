import { useState, useRef } from 'react';
import { datasetAPI } from '../api';

function FileUpload({ onSuccess, onError }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState('');
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // Validate file type
    if (!file.name.endsWith('.csv')) {
      onError('Please upload a CSV file');
      return;
    }

    setFileName(file.name);
    setUploading(true);

    try {
      console.log('Uploading file:', file.name, file.size);
      const response = await datasetAPI.uploadCSV(file);
      console.log('Upload response:', response.data);
      onSuccess(response.data);
      setFileName('');
    } catch (err) {
      console.error('Upload error:', err);
      console.error('Error response:', err.response);
      onError(err.response?.data?.error || err.message || 'Failed to upload file');
    } finally {
      setUploading(false);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    }
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div
      className={`upload-section ${dragActive ? 'drag-active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={onButtonClick}
    >
      <input
        ref={inputRef}
        type="file"
        className="file-input"
        accept=".csv"
        onChange={handleChange}
      />
      
      {uploading ? (
        <>
          <div className="spinner"></div>
          <p className="upload-text">Uploading {fileName}...</p>
        </>
      ) : (
        <>
          <div className="upload-icon">📁</div>
          <p className="upload-text">
            Drag & drop a CSV file here<br />
            or click to browse
          </p>
          <p style={{ fontSize: '0.8rem', color: '#999' }}>
            Supports: Equipment Name, Type, Flowrate, Pressure, Temperature
          </p>
        </>
      )}
    </div>
  );
}

export default FileUpload;
