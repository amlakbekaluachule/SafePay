import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h1>SafePay</h1>
        <p className="nav-subtitle">Fraud Detection</p>
      </div>
      <ul className="nav-menu">
        <li>
          <Link to="/" className={isActive('/')}>
            <span className="nav-icon">📊</span>
            Dashboard
          </Link>
        </li>
        <li>
          <Link to="/transactions" className={isActive('/transactions')}>
            <span className="nav-icon">💳</span>
            Transactions
          </Link>
        </li>
        <li>
          <Link to="/analytics" className={isActive('/analytics')}>
            <span className="nav-icon">📈</span>
            Analytics
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;

