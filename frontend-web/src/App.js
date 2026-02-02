import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import AuthPage from './components/AuthPage';
import { authAPI } from './api';
import './index.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.log('Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <Header user={user} onLogout={handleLogout} />
        <Routes>
          <Route 
            path="/" 
            element={<Dashboard user={user} />} 
          />
          <Route 
            path="/auth" 
            element={
              user ? <Navigate to="/" replace /> : <AuthPage onLogin={handleLogin} />
            } 
          />
        </Routes>
        <footer className="footer">
          <p>Chemical Equipment Parameter Visualizer © 2026</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
