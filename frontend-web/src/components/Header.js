import React from 'react';
import { Link } from 'react-router-dom';

function Header({ user, onLogout }) {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" style={{ textDecoration: 'none', color: 'white' }}>
          <h1>🔬 Chemical Equipment Parameter Visualizer</h1>
        </Link>
        <nav className="header-nav">
          {user ? (
            <>
              <span>Welcome, {user.username}</span>
              <button className="btn btn-outline" onClick={onLogout}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/auth">
              <button className="btn btn-outline">Login / Register</button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;
