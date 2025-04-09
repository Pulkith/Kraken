// components/TwitterFeed.js
import React from 'react';
import '../styles/TwitterFeed.css';

function TwitterFeed({ articles }) {

  function timeAgoFromTwitterFormat(twitterDateString) {
    const date = new Date(twitterDateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
  
    if (isNaN(seconds)) return "Invalid date";
  
    const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  
    const intervals = [
      { limit: 60, divisor: 1, unit: 'second' },
      { limit: 3600, divisor: 60, unit: 'minute' },
      { limit: 86400, divisor: 3600, unit: 'hour' },
      { limit: 604800, divisor: 86400, unit: 'day' },
      { limit: 2629800, divisor: 604800, unit: 'week' },
      { limit: 31557600, divisor: 2629800, unit: 'month' },
      { limit: Infinity, divisor: 31557600, unit: 'year' }
    ];
  
    for (const { limit, divisor, unit } of intervals) {
      if (seconds < limit) {
        const delta = Math.floor(seconds / divisor);
        return rtf.format(-delta, unit);
      }
    }
  
    return "some time ago";
  }
  
  return (
    <div className="twitter-feed">
      {articles.map(post => (
        <div key={post.id} className="twitter-post">
          <div className="post-header">
            <img src={"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcbbkAWH8ZnrfxzrRnUE7h1WHWmM6WHos3Ng&s"} alt={post.author} className="author-avatar" />
            <div className="author-info">
              <div className="author-name">{post.user_screen_name}</div>
              <div className="author-handle">{post.user_name}</div>
            </div>
            <div className="post-date">{timeAgoFromTwitterFormat(post.created_at)}</div>
          </div>
          <div className="post-content">{post.text}</div>
          <div className="post-actions">
            <div className="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>Reply</span>
            </div>
            <div className="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="17 1 21 5 17 9"></polyline>
                <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
                <polyline points="7 23 3 19 7 15"></polyline>
                <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
              </svg>
              <span>{post.retweets}</span>
            </div>
            <div className="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
              </svg>
              <span>{post.likes}</span>
            </div>
            <div className="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                <polyline points="16 6 12 2 8 6"></polyline>
                <line x1="12" y1="2" x2="12" y2="15"></line>
              </svg>
              <span>Share</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default TwitterFeed;