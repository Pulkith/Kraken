import React, { useState } from 'react';
import '../styles/PreferencesPage.css';

function PreferencesPage() {
  const [topics, setTopics] = useState([
    { id: 'blockchain', name: 'Blockchain', selected: true },
    { id: 'crypto', name: 'Cryptocurrency', selected: true },
    { id: 'web3', name: 'Web3', selected: true },
    { id: 'nft', name: 'NFTs', selected: false },
    { id: 'defi', name: 'DeFi', selected: true },
    { id: 'dao', name: 'DAOs', selected: false },
    { id: 'metaverse', name: 'Metaverse', selected: false },
    { id: 'regulation', name: 'Regulation', selected: true },
  ]);
  
  const [following, setFollowing] = useState([
    { id: 'vbuterin', name: 'Vitalik Buterin', handle: '@VitalikButerin', selected: true },
    { id: 'cz', name: 'CZ Binance', handle: '@cz_binance', selected: true },
    { id: 'elonmusk', name: 'Elon Musk', handle: '@elonmusk', selected: false },
    { id: 'saylor', name: 'Michael Saylor', handle: '@saylor', selected: true },
  ]);
  
  const [sources, setSources] = useState([
    { id: 'coindesk', name: 'CoinDesk', selected: true },
    { id: 'decrypt', name: 'Decrypt', selected: true },
    { id: 'theblock', name: 'The Block', selected: false },
    { id: 'cointelegraph', name: 'CoinTelegraph', selected: true },
  ]);
  
  const [systemPrompt, setSystemPrompt] = useState(
    "Generate a balanced daily digest focusing on factual reporting of blockchain news with verified sources only."
  );
  
  const handleTopicToggle = (id) => {
    setTopics(topics.map(topic => 
      topic.id === id ? { ...topic, selected: !topic.selected } : topic
    ));
  };
  
  const handleFollowToggle = (id) => {
    setFollowing(following.map(person => 
      person.id === id ? { ...person, selected: !person.selected } : person
    ));
  };
  
  const handleSourceToggle = (id) => {
    setSources(sources.map(source => 
      source.id === id ? { ...source, selected: !source.selected } : source
    ));
  };
  
  const [newPerson, setNewPerson] = useState({ name: '', handle: '' });
  
  const addPerson = () => {
    if (newPerson.name && newPerson.handle) {
      setFollowing([
        ...following, 
        { 
          id: `person-${Date.now()}`, 
          name: newPerson.name, 
          handle: newPerson.handle.startsWith('@') ? newPerson.handle : `@${newPerson.handle}`, 
          selected: true 
        }
      ]);
      setNewPerson({ name: '', handle: '' });
    }
  };
  
  return (
    <div className="preferences-container">
      <h1>Your Preferences</h1>
      <p>Customize your Kraken experience</p>
      
      <div className="preferences-grid">
        <div className="preference-card topics-card">
          <h2>Topics</h2>
          <p>Select topics you want to follow</p>
          
          <div className="topics-grid">
            {topics.map(topic => (
              <div 
                key={topic.id} 
                className={`topic-item ${topic.selected ? 'selected' : ''}`}
                onClick={() => handleTopicToggle(topic.id)}
              >
                {topic.name}
              </div>
            ))}
          </div>
        </div>
        
        <div className="preference-card people-card">
          <h2>People to Follow</h2>
          <p>Select influential people in the space</p>
          
          <div className="add-person">
            <input
              type="text"
              placeholder="Name"
              value={newPerson.name}
              onChange={(e) => setNewPerson({...newPerson, name: e.target.value})}
            />
            <input
              type="text"
              placeholder="X Handle"
              value={newPerson.handle}
              onChange={(e) => setNewPerson({...newPerson, handle: e.target.value})}
            />
            <button onClick={addPerson}>Add</button>
          </div>
          
          <ul className="following-list">
            {following.map(person => (
              <li key={person.id} className={person.selected ? 'selected' : ''}>
                <div className="person-info">
                  <div className="person-avatar">
                    {person.name.charAt(0)}
                  </div>
                  <div className="person-details">
                    <div className="person-name">{person.name}</div>
                    <div className="person-handle">{person.handle}</div>
                  </div>
                </div>
                <button 
                  className={`follow-btn ${person.selected ? 'following' : ''}`}
                  onClick={() => handleFollowToggle(person.id)}
                >
                  {person.selected ? 'Following' : 'Follow'}
                </button>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="preference-card sources-card">
          <h2>News Sources</h2>
          <p>Select your preferred news sources</p>
          
          <ul className="sources-list">
            {sources.map(source => (
              <li 
                key={source.id} 
                className={source.selected ? 'selected' : ''}
                onClick={() => handleSourceToggle(source.id)}
              >
                <span className="source-name">{source.name}</span>
                <span className="source-checkbox"></span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="preference-card prompt-card">
          <h2>System Prompt</h2>
          <p>Customize how Kraken generates content for you</p>
          
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={5}
            placeholder="Enter your custom system prompt..."
          />
          
          <div className="prompt-templates">
            <h3>Templates</h3>
            <button onClick={() => setSystemPrompt("Focus on technical blockchain developments with detailed analysis.")}>
              Technical Focus
            </button>
            <button onClick={() => setSystemPrompt("Summarize market trends and investment opportunities in the crypto space.")}>
              Investment Focus
            </button>
            <button onClick={() => setSystemPrompt("Highlight regulatory news and legal developments in blockchain.")}>
              Regulatory Focus
            </button>
          </div>
        </div>
      </div>
      
      <div className="save-preferences">
        <button className="save-btn">Save Preferences</button>
        <button className="reset-btn">Reset to Default</button>
      </div>
    </div>
  );
}

export default PreferencesPage;