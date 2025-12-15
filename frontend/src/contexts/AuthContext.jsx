import React, { createContext, useState, useEffect } from 'react';
import { isAuthenticated } from '../services/auth';
import { authAPI } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserInfo = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      console.log('User info from /auth/me:', response.data);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user info:', error);
      setUser(null);
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      if (isAuthenticated()) {
        await fetchUserInfo();
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (tokens) => {
    sessionStorage.setItem('access_token', tokens.access_token);
    sessionStorage.setItem('refresh_token', tokens.refresh_token);
    await fetchUserInfo(); // Получаем полную информацию после логина
  };

  const logout = () => {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
    isVerifiedAuthor: user?.is_verified_author || user?.is_admin || false,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};