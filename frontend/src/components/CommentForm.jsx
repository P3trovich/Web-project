import React, { useState } from 'react';
import { commentsAPI } from '../services/api';
import '../styles/CommentForm.css';

const CommentForm = ({ newsId, onCommentAdded }) => {
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Comment text is required');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await commentsAPI.createComment(newsId, {
        text: text.trim(),
      });
      
      setText('');
      setError('');
      
      if (onCommentAdded) {
        onCommentAdded();
      }
      
      window.location.reload();
    } catch (err) {
      console.error('Error creating comment:', err);
      setError('Failed to create comment');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="comment-form">
      <h3 className="comment-form-title">Add a Comment</h3>
      
      {error && <div className="form-error">{error}</div>}
      
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Write your comment here..."
        className="comment-textarea"
        rows="4"
        disabled={submitting}
      />
      
      <button 
        type="submit" 
        disabled={submitting || !text.trim()}
        className="submit-button"
      >
        {submitting ? 'Posting...' : 'Post Comment'}
      </button>
    </form>
  );
};

export default CommentForm;