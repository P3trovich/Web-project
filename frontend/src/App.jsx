import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/Header';
import NewsList from './components/NewsList';
import NewsDetail from './components/NewsDetail';
import LoginForm from './components/LoginForm';
import CreateNewsForm from './components/CreateNewsForm';
import EditNewsForm from './components/EditNewsForm';
import './index.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<NewsList />} />
              <Route path="/news/:id" element={<NewsDetail />} />
              <Route path="/news/:id/edit" element={<EditNewsForm />} /> {}
              <Route path="/login" element={<LoginForm />} />
              <Route path="/news/create" element={<CreateNewsForm />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;