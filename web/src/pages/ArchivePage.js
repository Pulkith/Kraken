// pages/ArchivePage.js
import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import '../styles/ArchivePage.css';
import NewsCard from '../components/NewsCard';

function ArchivePage() {
  const [pastDigests, setPastDigests] = useState([]);
  const [selectedDigest, setSelectedDigest] = useState(null);
  const [articles, setArticles] = useState([]);
  
  useEffect(() => {
    // Mock data for past digests
    const mockDigests = Array.from({ length: 14 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      return {
        id: `digest-${i}`,
        date: date,
        blockchainRef: `0x${Math.random().toString(16).slice(2, 10)}...${Math.random().toString(16).slice(2, 10)}`,
        articleCount: Math.floor(Math.random() * 3) + 6, // 6-8 articles
      };
    });
    
    setPastDigests(mockDigests);
  }, []);
  
  const handleDigestSelect = (digest) => {
    setSelectedDigest(digest);
    
    // Generate mock articles for the selected digest
    const mockArticles = Array.from({ length: digest.articleCount }, (_, i) => ({
      id: `article-${digest.id}-${i}`,
      title: `${['Breaking', 'Latest', 'Important'][i % 3]}: ${['Web3', 'Blockchain', 'Crypto', 'NFT', 'DeFi'][i % 5]} ${['News', 'Update', 'Development', 'Announcement'][i % 4]}`,
      summary: `This is a summary of the article about important developments in the blockchain space. The industry continues to evolve rapidly with new technologies emerging. Adoption rates are steadily increasing across various sectors. Regulatory frameworks are being developed in several countries. Investors remain cautiously optimistic about long-term prospects. Overall market sentiment has improved in recent weeks.`,
      image: `/api/placeholder/600/400`,
      date: format(digest.date, 'MMM d, yyyy'),
      author: ['Alice Blockchain', 'Bob Crypto', 'Charlie DeFi'][i % 3],
      mainSource: {
        name: ['CryptoNews', 'BlockchainDaily', 'Web3Insider'][i % 3],
        url: '#'
      },
      sources: [
        { name: 'TechCrunch', url: '#' },
        { name: 'CoinDesk', url: '#' }
      ],
      blockchainRef: digest.blockchainRef,
      hasPodcast: i % 3 === 0
    }));
    
    setArticles(mockArticles);
  };
  
  return (
    <div className="archive-container">
      <h1>Kraken Archive</h1>
      <p>Access all your past Krakbits, verified on the blockchain</p>
      
      <div className="archive-layout">
        <aside className="digest-list">
          <h2>Past Digests</h2>
          <ul>
            {pastDigests.map(digest => (
              <li 
                key={digest.id} 
                className={selectedDigest?.id === digest.id ? 'selected' : ''}
                onClick={() => handleDigestSelect(digest)}
              >
                <div className="digest-date">{format(digest.date, 'MMM d, yyyy')}</div>
                <div className="digest-info">
                  <span className="article-count">{digest.articleCount} articles</span>
                  {/* <span className="blockchain-ref" title={digest.blockchainRef}>
                    Block: {digest.blockchainRef.substring(0, 7)}...
                  </span> */}
                </div>
              </li>
            ))}
          </ul>
        </aside>
        
        <div className="digest-content">
          {selectedDigest ? (
            <>
              <div className="digest-header">
                <h2>Krakbit for {format(selectedDigest.date, 'MMMM d, yyyy')}</h2>
                <div className="blockchain-verification">
                  <span>Blockchain Transaction: </span>
                  <a href="#" className="transaction-link">{selectedDigest.blockchainRef}</a>
                  <div className="verified-badge">Verified</div>
                </div>
              </div>
              
              <div className="archive-news-grid">
                {articles.map(article => (
                  <NewsCard key={article.id} article={article} />
                ))}
              </div>
            </>
          ) : (
            <div className="no-selection">
              <p>Select a digest from the list to view its contents</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ArchivePage;