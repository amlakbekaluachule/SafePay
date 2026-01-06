import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { apiService, FraudTrend, Stats, ModelMetrics } from '../services/api';
import './Analytics.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Analytics: React.FC = () => {
  const [trends, setTrends] = useState<FraudTrend[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [timeWindow, setTimeWindow] = useState(24);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
    const interval = setInterval(loadAnalytics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeWindow]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [trendsData, statsData, metricsData] = await Promise.all([
        apiService.getFraudTrends(timeWindow),
        apiService.getStats(timeWindow),
        apiService.getModelMetrics()
      ]);
      setTrends(trendsData);
      setStats(statsData);
      setMetrics(metricsData);
      setLoading(false);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setLoading(false);
    }
  };

  const chartData = {
    labels: trends.map(t => new Date(t.hour).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Total Transactions',
        data: trends.map(t => t.total_transactions),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Fraud Transactions',
        data: trends.map(t => t.fraud_transactions),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const fraudRateData = {
    labels: trends.map(t => new Date(t.hour).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Fraud Rate (%)',
        data: trends.map(t => t.fraud_rate * 100),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <h1 className="page-title">Analytics</h1>
        <div className="time-window-selector">
          <label>Time Window:</label>
          <select value={timeWindow} onChange={(e) => setTimeWindow(Number(e.target.value))}>
            <option value={1}>Last Hour</option>
            <option value={6}>Last 6 Hours</option>
            <option value={24}>Last 24 Hours</option>
            <option value={48}>Last 48 Hours</option>
            <option value={168}>Last Week</option>
          </select>
        </div>
      </div>

      <div className="analytics-stats">
        <div className="stat-box">
          <h3>Fraud Rate</h3>
          <p className="stat-number">{(stats?.fraud_rate || 0) * 100}%</p>
          <p className="stat-detail">
            {stats?.fraud_transactions} of {stats?.total_transactions} transactions
          </p>
        </div>
        <div className="stat-box">
          <h3>Average Fraud Probability</h3>
          <p className="stat-number">{(metrics?.avg_fraud_probability || 0).toFixed(4)}</p>
          <p className="stat-detail">Model confidence</p>
        </div>
        <div className="stat-box">
          <h3>Average Inference Time</h3>
          <p className="stat-number">{(metrics?.avg_inference_time_ms || 0).toFixed(2)} ms</p>
          <p className="stat-detail">Real-time performance</p>
        </div>
        {metrics?.accuracy !== undefined && (
          <div className="stat-box">
            <h3>Model Accuracy</h3>
            <p className="stat-number">{(metrics.accuracy * 100).toFixed(2)}%</p>
            <p className="stat-detail">Based on ground truth</p>
          </div>
        )}
      </div>

      <div className="charts-container">
        <div className="chart-card">
          <h2>Transaction Volume & Fraud Detection</h2>
          <div className="chart-wrapper">
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <h2>Fraud Rate Over Time</h2>
          <div className="chart-wrapper">
            <Line data={fraudRateData} options={chartOptions} />
          </div>
        </div>
      </div>

      <div className="metrics-detail">
        <h2>Detailed Metrics</h2>
        <div className="metrics-grid">
          <div className="metric-item">
            <label>Total Predictions</label>
            <p>{metrics?.total_predictions.toLocaleString() || 0}</p>
          </div>
          <div className="metric-item">
            <label>Fraud Predictions</label>
            <p>{metrics?.fraud_predictions.toLocaleString() || 0}</p>
          </div>
          <div className="metric-item">
            <label>Total Amount Processed</label>
            <p>${(stats?.total_amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
          <div className="metric-item">
            <label>Fraud Amount</label>
            <p className="fraud-amount">${(stats?.fraud_amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

