import React, { useState, useEffect } from 'react';
import { apiService, Transaction, Prediction } from '../services/api';
import './Transactions.css';

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterFraud, setFilterFraud] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    loadTransactions();
  }, [filterFraud]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTransactions(100, undefined, filterFraud);
      setTransactions(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading transactions:', error);
      setLoading(false);
    }
  };

  const handleTransactionClick = async (txn: Transaction) => {
    setSelectedTransaction(txn);
    try {
      const pred = await apiService.getPrediction(txn.id);
      setPrediction(pred);
    } catch (error) {
      console.error('Error loading prediction:', error);
      setPrediction(null);
    }
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  return (
    <div className="transactions-page">
      <h1 className="page-title">Transactions</h1>

      <div className="filters">
        <button
          className={`filter-btn ${filterFraud === undefined ? 'active' : ''}`}
          onClick={() => setFilterFraud(undefined)}
        >
          All
        </button>
        <button
          className={`filter-btn ${filterFraud === true ? 'active' : ''}`}
          onClick={() => setFilterFraud(true)}
        >
          Fraud Only
        </button>
        <button
          className={`filter-btn ${filterFraud === false ? 'active' : ''}`}
          onClick={() => setFilterFraud(false)}
        >
          Safe Only
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading transactions...</div>
      ) : (
        <div className="transactions-container">
          <div className="transactions-list">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Amount</th>
                  <th>Merchant</th>
                  <th>Location</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr
                    key={txn.id}
                    onClick={() => handleTransactionClick(txn)}
                    className={selectedTransaction?.id === txn.id ? 'selected' : ''}
                  >
                    <td className="txn-id">{txn.id.substring(0, 12)}...</td>
                    <td>{txn.user_id.substring(0, 8)}...</td>
                    <td className="amount">{formatCurrency(txn.amount, txn.currency)}</td>
                    <td>{txn.merchant_category}</td>
                    <td>{txn.location_country}</td>
                    <td>{new Date(txn.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedTransaction && (
            <div className="transaction-details">
              <h2>Transaction Details</h2>
              <div className="detail-section">
                <h3>Transaction Info</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>ID</label>
                    <p>{selectedTransaction.id}</p>
                  </div>
                  <div className="detail-item">
                    <label>User ID</label>
                    <p>{selectedTransaction.user_id}</p>
                  </div>
                  <div className="detail-item">
                    <label>Amount</label>
                    <p className="amount-large">
                      {formatCurrency(selectedTransaction.amount, selectedTransaction.currency)}
                    </p>
                  </div>
                  <div className="detail-item">
                    <label>Merchant</label>
                    <p>{selectedTransaction.merchant_category}</p>
                  </div>
                  <div className="detail-item">
                    <label>Location</label>
                    <p>{selectedTransaction.location_country}</p>
                  </div>
                  <div className="detail-item">
                    <label>Time</label>
                    <p>{new Date(selectedTransaction.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              </div>

              {prediction && (
                <div className="detail-section">
                  <h3>Fraud Prediction</h3>
                  <div className="prediction-card">
                    <div className="prediction-header">
                      <span className={`fraud-badge ${prediction.is_fraud ? 'fraud' : 'safe'}`}>
                        {prediction.is_fraud ? '🚨 FRAUD' : '✅ SAFE'}
                      </span>
                      <span className="probability">
                        {(prediction.fraud_probability * 100).toFixed(2)}% probability
                      </span>
                    </div>
                    <div className="prediction-details">
                      <p><strong>Model Version:</strong> {prediction.model_version}</p>
                      <p><strong>Inference Time:</strong> {prediction.inference_time_ms.toFixed(2)} ms</p>
                      <p><strong>Threshold:</strong> {(prediction.threshold * 100).toFixed(0)}%</p>
                    </div>

                    {prediction.explainability && (
                      <div className="explainability-section">
                        <h4>Top Contributing Features</h4>
                        <div className="feature-contributions">
                          {Object.entries(prediction.explainability.feature_contributions || {})
                            .slice(0, 5)
                            .map(([feature, data]: [string, any]) => (
                              <div key={feature} className="feature-item">
                                <div className="feature-name">{feature}</div>
                                <div className="feature-impact">
                                  <span className={`impact ${data.contribution}`}>
                                    {data.contribution === 'increases' ? '↑' : '↓'}
                                  </span>
                                  {data.impact.toFixed(4)}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Transactions;

