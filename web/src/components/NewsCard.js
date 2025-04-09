import React, { useState } from 'react';
import '../styles/NewsCard.css';

function NewsCard({ article }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSources, setShowSources] = useState(false);
  
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
    // Here you would implement the actual podcast playback
  };
  
  const toggleSources = (e) => {
    e.stopPropagation();
    setShowSources(!showSources);
  };
  
  return (
    <div 
      className={`news-card ${isExpanded ? 'expanded' : ''}`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="card-image-container">
        {/* <img src={article.image} alt={article.title} className="card-image" /> */}
        {article.hasPodcast && (
          <button 
            className={`podcast-button ${isPlaying ? 'playing' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              togglePlay();
            }}
          >
            {isPlaying ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            )}
            {isPlaying ? 'Pause' : 'Listen'}
          </button>
        )}
      </div>
      
      <div className="card-content">
        <h3 className="card-title">{article.title}</h3>
        
        <div className="card-meta">
          <span className="card-date">{article.date}</span>
          {/* <span className="card-author">By {article.author}</span> */}
        </div>
        
        <p className="card-summary">{article.summary}</p>
        
        <div className="card-actions">
          <button 
            className="sources-button"
            onClick={toggleSources}
          >
            Sources
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          
          <div className="blockchain-badge" title={`Transaction: ${article.blockchainRef}`}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            Verified
          </div>
        </div>
        
        {showSources && (
          <div className="sources-list" onClick={(e) => e.stopPropagation()}>
            <div className="main-source">
              <strong>Main Source:</strong> 
              <a href={article.mainSource.url} target="_blank" rel="noopener noreferrer">
                {article.mainSource.name}
              </a>
            </div>
            <ul>
              {article.sources.map((source, idx) => (
                <li key={idx}>
                  <a href={source.url} target="_blank" rel="noopener noreferrer">
                    {source.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {isExpanded && (
        <div className="ask-question">
          <input type="text" placeholder="Ask a follow-up question..." />
          <button>Ask</button>
        </div>
      )}
    </div>
  );
}

export default NewsCard;