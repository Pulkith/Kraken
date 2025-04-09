// App.js - Main component that handles routing and layout
import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ArchivePage from './pages/ArchivePage';
import PreferencesPage from './pages/PreferencesPage';
import AboutPage from './pages/AboutPage';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="header">
          <div className="logo">
            <NavLink to="/">
              <h1>Kraken</h1>
            </NavLink>
          </div>
          <nav className="main-nav">
            <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink>
            <NavLink to="/archive" className={({ isActive }) => isActive ? 'active' : ''}>Archive</NavLink>
            <NavLink to="/preferences" className={({ isActive }) => isActive ? 'active' : ''}>Preferences</NavLink>
            <NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>About</NavLink>
          </nav>
          <div className="user-controls">
            <button className="connect-wallet-btn">Wallet <div style={{
              backgroundColor: 'lightgray',
              padding: '4px 8px',
              borderRadius: '20px',
              color: "rgb(42, 42, 42)",
              fontSize: '12px',
              fontWeight: 'bold',
            }}>0xa03c...a9bd</div></button>
          </div>
        </header>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/archive" element={<ArchivePage />} />
            <Route path="/preferences" element={<PreferencesPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
        
        <footer className="footer">
          <div className="footer-content">
            <p>&copy; {new Date().getFullYear()} Kraken - Blockchain News Platform</p>
            <div className="footer-links">
              <a href="#">Terms</a>
              <a href="#">Privacy</a>
              <a href="#">Contact</a>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;