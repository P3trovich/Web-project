import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { newsAPI } from '../services/api';
import CommentList from './CommentList';
import CommentForm from './CommentForm';
import '../styles/NewsDetail.css';

const NewsDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [news, setNews] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchNews = async () => {
    try {
      const response = await newsAPI.getNewsById(id);
      setNews(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('News not found');
      } else {
        setError('Failed to load news');
      }
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, [id]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchNews();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [id]);

  const handleDeleteNews = async () => {
    if (!window.confirm('Are you sure you want to delete this news?')) {
      return;
    }

    try {
      await newsAPI.deleteNews(id);
      navigate('/');
    } catch (err) {
      console.error('Error deleting news:', err);
      alert('Failed to delete news');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const canEditNews = user?.is_admin || news?.author_id === user?.id;
  const canDeleteNews = user?.is_admin || news?.author_id === user?.id;

  if (loading) return <div className="loading">Loading news...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!news) return <div className="error">News not found</div>;

  return (
    <div className="news-detail-container">
      <article className="news-article">
        <header className="news-header">
          <h1 className="news-detail-title">{news.title}</h1>
          <div className="news-meta">
            <span>Published: {formatDate(news.publication_date)}</span>
            {news.author_id && <span> • Author ID: {news.author_id}</span>}
          </div>
          {(canEditNews || canDeleteNews) && (
            <div className="news-actions">
              {canEditNews && (
                <button 
                  className="edit-button"
                  onClick={() => navigate(`/news/${id}/edit`)}
                >
                  Edit
                </button>
              )}
              {canDeleteNews && (
                <button 
                  className="delete-button"
                  onClick={handleDeleteNews}
                >
                  Delete
                </button>
              )}
            </div>
          )}
        </header>
        
        {news.cover_image && (
          <img 
            src={news.cover_image} 
            alt={news.title}
            className="cover-image"
          />
        )}
        
        <div className="news-content">
          {news.content.split('\n').map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      </article>

      <section className="comments-section">
        <h2 className="comments-title">Comments</h2>
        <CommentList newsId={id} />
        {isAuthenticated ? (
          <CommentForm newsId={id} />
        ) : (
          <div className="login-prompt">
            Please <a href="/login" className="login-link">login</a> to leave a comment
          </div>
        )}
      </section>
    </div>
  );
};

export default NewsDetail;