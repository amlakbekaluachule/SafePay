import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Transaction {
  id: string;
  user_id: string;
  card_id: string;
  amount: number;
  currency: string;
  merchant_id: string;
  merchant_category: string;
  transaction_type: string;
  location_country: string;
  location_city?: string;
  timestamp: string;
  created_at: string;
}

export interface Prediction {
  transaction_id: string;
  fraud_probability: number;
  is_fraud: boolean;
  threshold: number;
  model_version: string;
  inference_time_ms: number;
  explainability?: {
    shap_values: Record<string, number>;
    feature_contributions: Record<string, any>;
  };
}

export interface TransactionRequest {
  user_id: string;
  card_id: string;
  amount: number;
  currency?: string;
  merchant_id: string;
  merchant_category: string;
  transaction_type?: string;
  location_country: string;
  location_city?: string;
  ip_address?: string;
  device_id?: string;
  threshold?: number;
  include_explainability?: boolean;
}

export interface Stats {
  total_transactions: number;
  fraud_transactions: number;
  fraud_rate: number;
  total_amount: number;
  fraud_amount: number;
  time_window_hours: number;
}

export interface ModelMetrics {
  total_predictions: number;
  fraud_predictions: number;
  fraud_rate: number;
  avg_fraud_probability: number;
  avg_inference_time_ms: number;
  accuracy?: number;
}

export interface FraudTrend {
  hour: string;
  total_transactions: number;
  fraud_transactions: number;
  fraud_rate: number;
}

export const apiService = {
  // Predictions
  predictFraud: async (transaction: TransactionRequest): Promise<Prediction> => {
    const response = await api.post('/predictions/', transaction);
    return response.data;
  },

  getPrediction: async (transactionId: string): Promise<Prediction> => {
    const response = await api.get(`/predictions/${transactionId}`);
    return response.data;
  },

  // Transactions
  getTransactions: async (limit?: number, user_id?: string, is_fraud?: boolean): Promise<Transaction[]> => {
    const params: any = {};
    if (limit) params.limit = limit;
    if (user_id) params.user_id = user_id;
    if (is_fraud !== undefined) params.is_fraud = is_fraud;
    
    const response = await api.get('/transactions/', { params });
    return response.data;
  },

  getTransaction: async (transactionId: string): Promise<Transaction> => {
    const response = await api.get(`/transactions/${transactionId}`);
    return response.data;
  },

  // Analytics
  getStats: async (hours: number = 24): Promise<Stats> => {
    const response = await api.get('/analytics/stats', { params: { hours } });
    return response.data;
  },

  getModelMetrics: async (modelVersion?: string): Promise<ModelMetrics> => {
    const params: any = {};
    if (modelVersion) params.model_version = modelVersion;
    
    const response = await api.get('/analytics/model-metrics', { params });
    return response.data;
  },

  getFraudTrends: async (hours: number = 24): Promise<FraudTrend[]> => {
    const response = await api.get('/analytics/fraud-trends', { params: { hours } });
    return response.data;
  },
};

export default api;

