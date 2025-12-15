import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { newsAPI } from '../services/api';
import '../styles/NewsList.css';

const NewsList = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await newsAPI.getNews();
        console.log('Received news data:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          setNews(response.data);
        } else {
          setError('Invalid data format received from server');
        }
      } catch (err) {
        console.error('Error fetching news:', err);
        setError('Failed to load news: ' + (err.message || 'Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateString;
    }
  };

  if (loading) return <div className="loading">Loading news...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="news-container">
      <h1 className="news-title">Latest News</h1>
      <div className="news-grid">
        {news.map((item) => (
          <div key={item.id} className="news-card">
            <Link to={`/news/${item.id}`} className="news-link">
              <h3 className="news-item-title">{item.title || 'No title'}</h3>
              <p className="email">
                Author ID: {item.author_id}
              </p>
              <p className="news-date">
                Published: {formatDate(item.publication_date)}
              </p>
            </Link>
          </div>
        ))}
      </div>
      {news.length === 0 && !loading && (
        <div className="no-news">No news available</div>
      )}
    </div>
  );
};

export default NewsList;