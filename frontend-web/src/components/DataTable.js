function DataTable({ records }) {
  if (!records || records.length === 0) {
    return <p>No records to display</p>;
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Equipment Name</th>
            <th>Type</th>
            <th>Flowrate</th>
            <th>Pressure</th>
            <th>Temperature</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record, index) => (
            <tr key={record.id || index}>
              <td>{index + 1}</td>
              <td>{record.equipment_name}</td>
              <td>{record.equipment_type}</td>
              <td>{record.flowrate}</td>
              <td>{record.pressure}</td>
              <td>{record.temperature}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
