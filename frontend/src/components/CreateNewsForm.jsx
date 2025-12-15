import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { newsAPI } from '../services/api';
import '../styles/CreateNewsForm.css';

const CreateNewsForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    cover_image: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { isVerifiedAuthor } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isVerifiedAuthor) {
      setError('You need to be a verified author to create news');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await newsAPI.createNews(formData);
      navigate('/');
    } catch (err) {
      console.error('Error creating news:', err);
      setError(err.response?.data?.detail || 'Failed to create news');
    } finally {
      setLoading(false);
    }
  };

  if (!isVerifiedAuthor) {
    return (
      <div className="create-news-container">
        <div className="create-news-form">
          <div className="create-news-error">
            You need to be a verified author to create news articles.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="create-news-container">
      <form onSubmit={handleSubmit} className="create-news-form">
        <h2 className="create-news-title">Create New News Article</h2>
        
        {error && <div className="create-news-error">{error}</div>}
        
        <div className="create-news-form-group">
          <label htmlFor="title" className="create-news-label">
            Title:
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="create-news-input"
            disabled={loading}
          />
        </div>
        
        <div className="create-news-form-group">
          <label htmlFor="content" className="create-news-label">
            Content:
          </label>
          <textarea
            id="content"
            name="content"
            value={formData.content}
            onChange={handleChange}
            required
            className="create-news-textarea"
            disabled={loading}
            rows="10"
          />
        </div>
        
        <div className="create-news-form-group">
          <label htmlFor="cover_image" className="create-news-label">
            Cover Image URL (optional):
          </label>
          <input
            type="url"
            id="cover_image"
            name="cover_image"
            value={formData.cover_image}
            onChange={handleChange}
            className="create-news-input"
            disabled={loading}
            placeholder="https://example.com/image.jpg"
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          className="create-news-submit-button"
        >
          {loading ? 'Creating...' : 'Create News'}
        </button>
      </form>
    </div>
  );
};

export default CreateNewsForm;