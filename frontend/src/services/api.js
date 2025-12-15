import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Интерцептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Удаляем токены и перенаправляем на страницу входа
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const newsAPI = {
  getNews: () => 
    api.get('/news/'),
  
  getNewsById: (newsId) => 
    api.get(`/news/${newsId}`),
  
  createNews: (newsData) => 
    api.post('/news/', newsData),
  
  updateNews: (newsId, newsData) => 
    api.put(`/news/${newsId}`, newsData),
  
  deleteNews: (newsId) => 
    api.delete(`/news/${newsId}`),
  
  getNewsComments: (newsId) => 
    api.get(`/news/${newsId}/comments/`),
};

export const commentsAPI = {
  createComment: (newsId, commentData) => 
    api.post(`/news/${newsId}/comments/`, commentData),
  
  updateComment: (commentId, commentData) => 
    api.put(`/comments/${commentId}`, commentData),
  
  deleteComment: (commentId) => 
    api.delete(`/comments/${commentId}`),
};

export const authAPI = {
  login: (credentials) => 
    api.post('/auth/login', credentials),
  
  logout: () => {
    const refreshToken = sessionStorage.getItem('refresh_token');
    return axios.post(`${API_BASE_URL}/auth/logout`, {}, {
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    });
  },

  getCurrentUser: () => 
    api.get('/auth/me'),
};

export default api;