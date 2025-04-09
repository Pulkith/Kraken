import React, { useState } from 'react';
import '../styles/SearchBar.css';

function SearchBar({innerQ}) {
  const [searchTerm, setSearchTerm] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Searching for:', searchTerm);
    innerQ(searchTerm)
    // Here you would implement the search functionality
  };
  
  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} style={{width: "100%", display: 'flex', justifyContent: 'center'}}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Search for blockchain news, topics, or people..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit" className="search-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}

export default SearchBar;