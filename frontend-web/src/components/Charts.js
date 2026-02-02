import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Charts({ summary, records }) {
  if (!summary || !records) {
    return null;
  }

  // Colors for charts
  const colors = [
    'rgba(25, 118, 210, 0.8)',
    'rgba(76, 175, 80, 0.8)',
    'rgba(255, 152, 0, 0.8)',
    'rgba(156, 39, 176, 0.8)',
    'rgba(244, 67, 54, 0.8)',
    'rgba(0, 188, 212, 0.8)',
    'rgba(255, 193, 7, 0.8)',
    'rgba(96, 125, 139, 0.8)',
  ];

  const borderColors = colors.map(c => c.replace('0.8', '1'));

  // Equipment Type Distribution (Pie Chart)
  const typeDistribution = summary.type_distribution || {};
  const pieData = {
    labels: Object.keys(typeDistribution),
    datasets: [
      {
        data: Object.values(typeDistribution),
        backgroundColor: colors.slice(0, Object.keys(typeDistribution).length),
        borderColor: borderColors.slice(0, Object.keys(typeDistribution).length),
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: false,
      },
    },
  };

  // Average by Type (Bar Chart)
  const typeAverages = summary.type_averages || {};
  const barData = {
    labels: Object.keys(typeAverages),
    datasets: [
      {
        label: 'Avg. Flowrate',
        data: Object.values(typeAverages).map(t => t.avg_flowrate),
        backgroundColor: 'rgba(25, 118, 210, 0.7)',
        borderColor: 'rgba(25, 118, 210, 1)',
        borderWidth: 1,
      },
      {
        label: 'Avg. Pressure',
        data: Object.values(typeAverages).map(t => t.avg_pressure),
        backgroundColor: 'rgba(76, 175, 80, 0.7)',
        borderColor: 'rgba(76, 175, 80, 1)',
        borderWidth: 1,
      },
      {
        label: 'Avg. Temperature',
        data: Object.values(typeAverages).map(t => t.avg_temperature),
        backgroundColor: 'rgba(255, 152, 0, 0.7)',
        borderColor: 'rgba(255, 152, 0, 1)',
        borderWidth: 1,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  // Parameter Comparison Line Chart
  const lineData = {
    labels: records.slice(0, 15).map(r => r.equipment_name.split('-')[0]),
    datasets: [
      {
        label: 'Flowrate',
        data: records.slice(0, 15).map(r => r.flowrate),
        borderColor: 'rgba(25, 118, 210, 1)',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Pressure',
        data: records.slice(0, 15).map(r => r.pressure),
        borderColor: 'rgba(76, 175, 80, 1)',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Temperature',
        data: records.slice(0, 15).map(r => r.temperature),
        borderColor: 'rgba(255, 152, 0, 1)',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="charts-grid">
      <div className="chart-container">
        <h4 className="chart-title">Equipment Type Distribution</h4>
        <Pie data={pieData} options={pieOptions} />
      </div>

      <div className="chart-container">
        <h4 className="chart-title">Average Parameters by Type</h4>
        <Bar data={barData} options={barOptions} />
      </div>

      <div className="chart-container" style={{ gridColumn: 'span 2' }}>
        <h4 className="chart-title">Parameter Comparison (First 15 Equipment)</h4>
        <Line data={lineData} options={lineOptions} />
      </div>
    </div>
  );
}

export default Charts;
