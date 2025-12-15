import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authAPI } from '../services/api';
import '../styles/Header.css';

const Header = () => {
  const { user, logout, isAuthenticated, isVerifiedAuthor } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      navigate('/');
    }
  };

  return (
    <header className="header">
      <nav className="nav">
        <Link to="/" className="logo">
          News Service
        </Link>
        
        <div className="nav-links">
          {isAuthenticated ? (
            <>
              {}
              {isVerifiedAuthor && (
                <Link to="/news/create" className="nav-link">
                  Create News
                </Link>
              )}
              <span className="user-info">
                Welcome, {user?.email}
                {user?.is_admin && ' (Admin)'}
                {user?.is_verified_author && !user?.is_admin && ' (Author)'}
              </span>
              <button onClick={handleLogout} className="logout-button">
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="nav-link">
              Login
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;