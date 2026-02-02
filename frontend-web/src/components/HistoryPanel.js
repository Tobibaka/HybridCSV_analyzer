function HistoryPanel({ datasets, currentDataset, onSelect, onDelete, onDownload }) {
  if (!datasets || datasets.length === 0) {
    return (
      <p style={{ color: '#666', textAlign: 'center', padding: '1rem' }}>
        No datasets uploaded yet
      </p>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <ul className="history-list">
      {datasets.map((dataset) => (
        <li
          key={dataset.id}
          className={`history-item ${currentDataset === dataset.id ? 'active' : ''}`}
          onClick={() => onSelect(dataset.id)}
        >
          <div className="history-info">
            <h4>{dataset.name}</h4>
            <p>{formatDate(dataset.uploaded_at)}</p>
            <p>{dataset.total_records} records</p>
          </div>
          <div className="history-actions">
            <button
              className="btn btn-success"
              onClick={(e) => {
                e.stopPropagation();
                onDownload(dataset.id);
              }}
              title="Download PDF"
            >
              📥
            </button>
            <button
              className="btn btn-danger"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(dataset.id);
              }}
              title="Delete"
            >
              🗑️
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default HistoryPanel;
