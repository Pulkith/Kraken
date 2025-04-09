// pages/AboutPage.js
import React from 'react';
import '../styles/AboutPage.css';

function AboutPage() {
  return (
    <div className="about-container">
      <div className="about-header">
        <h1>About Kraken</h1>
        <p>A blockchain-powered news platform for verified, transparent journalism</p>
      </div>
      
      <div className="about-section">
        <h2>Our Mission</h2>
        <p>
          Kraken was created to solve the growing problem of misinformation in digital media. 
          By leveraging blockchain technology, we provide a transparent, verifiable news digest 
          that empowers readers to trace information back to its source.
        </p>
      </div>
      
      <div className="about-grid">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Source Verification</h3>
          <p>
            Every article and piece of information is tracked on the blockchain, 
            allowing you to verify the authenticity and origin of all content.
          </p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon">🤖</div>
          <h3>AI-Powered Summaries</h3>
          <p>
            Our advanced AI creates concise summaries of complex news stories,
            making it easier to digest information without losing context.
          </p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon">🔊</div>
          <h3>Podcast Conversion</h3>
          <p>
            Listen to your daily news digest on the go with automatic
            podcast conversion of all articles.
          </p>
        </div>
        
        <div className="feature-card">
          <div className="feature-icon">💬</div>
          <h3>Interactive Q&A</h3>
          <p>
            Ask follow-up questions about any news story using
            our advanced voice interface.
          </p>
        </div>
      </div>
      
      <div className="tech-section">
        <h2>Our Technology</h2>
        <p>
          Kraken uses a combination of blockchain verification, AI summarization, and
          web3 technologies to create a trustworthy news ecosystem.
        </p>
        
        <div className="tech-details">
          <div className="tech-item">
            <h3>Smart Contracts</h3>
            <p>
              All content references are stored on-chain using smart contracts,
              creating an immutable record of news sources and content.
            </p>
          </div>
          
          <div className="tech-item">
            <h3>Decentralized Storage</h3>
            <p>
              Content is stored across decentralized networks,
              ensuring censorship resistance and availability.
            </p>
          </div>
          
          <div className="tech-item">
            <h3>AI Processing</h3>
            <p>
              Advanced language models process and summarize news from 
              verified sources while maintaining accuracy.
            </p>
          </div>
        </div>
      </div>
      
      <div className="team-section">
        <h2>Built for BUIDL ASIA 2025!</h2>
        <p>
          Kraken was created by a team of blockchain enthusiasts and 
          journalists who believe in a future where information is transparent,
          verifiable, and accessible to all.
        </p>
      </div>
    </div>
  );
}

export default AboutPage;