import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { commentsAPI, newsAPI } from '../services/api';
import '../styles/CommentList.css';

const CommentList = ({ newsId }) => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    fetchComments();
  }, [newsId]);

  const fetchComments = async () => {
    try {
      const response = await newsAPI.getNewsComments(newsId);
      setComments(response.data);
    } catch (err) {
      setError('Failed to load comments');
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    try {
      await commentsAPI.deleteComment(commentId);
      setComments(comments.filter(comment => comment.id !== commentId));
    } catch (err) {
      console.error('Error deleting comment:', err);
      alert('Failed to delete comment');
    }
  };

  const startEdit = (comment) => {
    setEditingCommentId(comment.id);
    setEditText(comment.text);
  };

  const cancelEdit = () => {
    setEditingCommentId(null);
    setEditText('');
  };

  const saveEdit = async (commentId) => {
    try {
      const response = await commentsAPI.updateComment(commentId, {
        text: editText,
      });
      
      setComments(comments.map(comment => 
        comment.id === commentId ? response.data : comment
      ));
      cancelEdit();
    } catch (err) {
      console.error('Error updating comment:', err);
      alert('Failed to update comment');
    }
  };

  const canEditComment = (commentAuthorId) => {
    return user?.is_admin || user?.id === commentAuthorId;
  };

  const canDeleteComment = (commentAuthorId) => {
    return user?.is_admin || user?.id === commentAuthorId;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) return <div className="loading">Loading comments...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="comments-list">
      {comments.map((comment) => (
        <div key={comment.id} className="comment-card">
          {editingCommentId === comment.id ? (
            <div className="edit-form">
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="edit-textarea"
                rows="3"
              />
              <div className="edit-actions">
                <button 
                  onClick={() => saveEdit(comment.id)}
                  className="save-button"
                >
                  Save
                </button>
                <button 
                  onClick={cancelEdit}
                  className="cancel-button"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="comment-header">
                <span className="comment-author-info">
                  Author ID: {comment.author_id}  
                  <br />
                  <span className="comment-date">Published: {formatDate(comment.publication_date)}</span>
                </span>
                {(canEditComment(comment.author_id) || canDeleteComment(comment.author_id)) && (
                  <div className="comment-actions">
                    {canEditComment(comment.author_id) && (
                      <button 
                        onClick={() => startEdit(comment)}
                        className="comment-edit-button"
                      >
                        Edit
                      </button>
                    )}
                    {canDeleteComment(comment.author_id) && (
                      <button 
                        onClick={() => handleDeleteComment(comment.id)}
                        className="comment-delete-button"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                )}
              </div>
              <p className="comment-text">{comment.text}</p>
            </>
          )}
        </div>
      ))}
      {comments.length === 0 && (
        <div className="no-comments">No comments yet. Be the first to comment!</div>
      )}
    </div>
  );
};

export default CommentList;