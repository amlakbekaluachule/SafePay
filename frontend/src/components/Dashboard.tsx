import React, { useState, useEffect } from 'react';
import { apiService, Stats, ModelMetrics, Transaction } from '../services/api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsData, metricsData, transactionsData] = await Promise.all([
        apiService.getStats(24),
        apiService.getModelMetrics(),
        apiService.getTransactions(10)
      ]);
      setStats(statsData);
      setMetrics(metricsData);
      setRecentTransactions(transactionsData);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1 className="dashboard-title">Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💳</div>
          <div className="stat-content">
            <h3>Total Transactions</h3>
            <p className="stat-value">{stats?.total_transactions.toLocaleString() || 0}</p>
            <p className="stat-label">Last 24 hours</p>
          </div>
        </div>

        <div className="stat-card fraud">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>Fraud Detected</h3>
            <p className="stat-value">{stats?.fraud_transactions.toLocaleString() || 0}</p>
            <p className="stat-label">
              {(stats?.fraud_rate || 0) * 100}% fraud rate
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Total Amount</h3>
            <p className="stat-value">${(stats?.total_amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            <p className="stat-label">Last 24 hours</p>
          </div>
        </div>

        <div className="stat-card fraud">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>Fraud Amount</h3>
            <p className="stat-value">${(stats?.fraud_amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            <p className="stat-label">At risk</p>
          </div>
        </div>
      </div>

      <div className="metrics-section">
        <h2>Model Performance</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Average Fraud Probability</h4>
            <p className="metric-value">
              {(metrics?.avg_fraud_probability || 0).toFixed(4)}
            </p>
          </div>
          <div className="metric-card">
            <h4>Inference Time</h4>
            <p className="metric-value">
              {(metrics?.avg_inference_time_ms || 0).toFixed(2)} ms
            </p>
          </div>
          <div className="metric-card">
            <h4>Total Predictions</h4>
            <p className="metric-value">
              {(metrics?.total_predictions || 0).toLocaleString()}
            </p>
          </div>
          {metrics?.accuracy !== undefined && (
            <div className="metric-card">
              <h4>Accuracy</h4>
              <p className="metric-value">
                {(metrics.accuracy * 100).toFixed(2)}%
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="recent-transactions-section">
        <h2>Recent Transactions</h2>
        <div className="transactions-table">
          <table>
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>User ID</th>
                <th>Amount</th>
                <th>Merchant</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((txn) => (
                <tr key={txn.id}>
                  <td className="txn-id">{txn.id.substring(0, 8)}...</td>
                  <td>{txn.user_id.substring(0, 8)}...</td>
                  <td>${txn.amount.toFixed(2)}</td>
                  <td>{txn.merchant_category}</td>
                  <td>{new Date(txn.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

