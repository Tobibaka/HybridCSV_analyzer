import { useState, useEffect, useCallback } from 'react';
import { datasetAPI } from '../api';
import FileUpload from './FileUpload';
import DataTable from './DataTable';
import Charts from './Charts';
import HistoryPanel from './HistoryPanel';

function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [currentDataset, setCurrentDataset] = useState(null);
  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadDatasets = useCallback(async () => {
    try {
      const response = await datasetAPI.getAll();
      setDatasets(response.data);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    }
  }, []);

  useEffect(() => {
    loadDatasets();
  }, [loadDatasets]);

  const loadDatasetDetails = async (datasetId) => {
    setLoading(true);
    setError('');
    
    try {
      const [summaryRes, recordsRes] = await Promise.all([
        datasetAPI.getSummary(datasetId),
        datasetAPI.getRecords(datasetId)
      ]);
      
      setCurrentDataset(datasetId);
      setSummary(summaryRes.data);
      setRecords(recordsRes.data);
    } catch (err) {
      setError('Failed to load dataset details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (data) => {
    setSuccess('File uploaded successfully!');
    setTimeout(() => setSuccess(''), 3000);
    
    // Refresh datasets and load the new one
    loadDatasets();
    setCurrentDataset(data.id);
    setSummary(data.summary);
    setRecords(data.records);
  };

  const handleUploadError = (errorMsg) => {
    setError(errorMsg);
    setTimeout(() => setError(''), 5000);
  };

  const handleDeleteDataset = async (datasetId) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) return;
    
    try {
      await datasetAPI.delete(datasetId);
      setSuccess('Dataset deleted successfully!');
      setTimeout(() => setSuccess(''), 3000);
      
      // Refresh datasets
      if (currentDataset === datasetId) {
        setCurrentDataset(null);
        setSummary(null);
        setRecords([]);
      }
      loadDatasets();
    } catch (err) {
      setError('Failed to delete dataset');
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleDownloadReport = (datasetId) => {
    window.open(datasetAPI.downloadReport(datasetId), '_blank');
  };

  return (
    <main className="main-container">
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1.5rem' }}>
        {/* Left Sidebar - Upload & History */}
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">📤 Upload CSV</h3>
            </div>
            <FileUpload 
              onSuccess={handleUploadSuccess} 
              onError={handleUploadError}
            />
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="card-title">📜 Recent Datasets</h3>
            </div>
            <HistoryPanel
              datasets={datasets}
              currentDataset={currentDataset}
              onSelect={loadDatasetDetails}
              onDelete={handleDeleteDataset}
              onDownload={handleDownloadReport}
            />
          </div>
        </div>

        {/* Main Content Area */}
        <div>
          {loading ? (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
              </div>
            </div>
          ) : summary ? (
            <>
              {/* Summary Cards */}
              <div className="summary-grid">
                <div className="summary-card blue">
                  <div className="summary-value">{summary.total_count}</div>
                  <div className="summary-label">Total Equipment</div>
                </div>
                <div className="summary-card green">
                  <div className="summary-value">{summary.averages?.flowrate || 'N/A'}</div>
                  <div className="summary-label">Avg. Flowrate</div>
                </div>
                <div className="summary-card orange">
                  <div className="summary-value">{summary.averages?.pressure || 'N/A'}</div>
                  <div className="summary-label">Avg. Pressure</div>
                </div>
                <div className="summary-card purple">
                  <div className="summary-value">{summary.averages?.temperature || 'N/A'}</div>
                  <div className="summary-label">Avg. Temperature</div>
                </div>
              </div>

              {/* Charts */}
              <Charts summary={summary} records={records} />

              {/* Data Table */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">📊 Equipment Data</h3>
                  <button 
                    className="btn btn-success"
                    onClick={() => handleDownloadReport(currentDataset)}
                  >
                    📥 Download PDF Report
                  </button>
                </div>
                <DataTable records={records} />
              </div>
            </>
          ) : (
            <div className="card">
              <div className="alert alert-info">
                Upload a CSV file or select a dataset from history to view data and charts.
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default Dashboard;
