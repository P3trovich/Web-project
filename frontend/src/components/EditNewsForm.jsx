import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { newsAPI } from '../services/api';
import '../styles/CreateNewsForm.css';

const EditNewsForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    cover_image: '',
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await newsAPI.getNewsById(id);
        const news = response.data;
        
        // Проверяем права на редактирование
        if (news.author_id !== user?.id && !user?.is_admin) {
          setError('You do not have permission to edit this news');
          setLoading(false);
          return;
        }

        setFormData({
          title: news.title,
          content: news.content,
          cover_image: news.cover_image || '',
        });
      } catch (err) {
        setError('Failed to load news');
        console.error('Error fetching news:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [id, user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted, data:', formData);
    setSubmitting(true);
    setError('');

    try {
      console.log('Sending update request...');
      const response = await newsAPI.updateNews(id, formData);
      console.log('Update successful:', response);
      navigate(`/news/${id}`);
    } catch (err) {
      console.error('Error updating news:', err);
      console.error('Error details:', err.response);
      setError(err.response?.data?.detail || 'Failed to update news');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !formData.title) return <div className="error">{error}</div>;

  return (
    <div className="create-news-container">
      <form onSubmit={handleSubmit} className="create-news-form">
        <h2 className="create-news-title">Edit News Article</h2>
        
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
            placeholder="https://example.com/image.jpg"
          />
        </div>
        
        <div className="form-buttons">
          <button 
            type="submit" 
            className="create-news-submit-button"
          >
            Update News
          </button>
          
          <button 
            type="button"
            onClick={() => navigate(`/news/${id}`)}
            className="cancel-button"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditNewsForm;