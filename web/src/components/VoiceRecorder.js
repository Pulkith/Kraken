// components/VoiceRecorder.js
import React, { useState, useEffect } from 'react';
import '../styles/VoiceRecorder.css';

function VoiceRecorder({ onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingText, setRecordingText] = useState('');
  
  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    
    return () => clearInterval(interval);
  }, [isRecording]);
  
  const startRecording = () => {
    setIsRecording(true);
    setRecordingTime(0);
    
    // Simulate recording and speech recognition
    setTimeout(() => {
      const mockTexts = [
        "Can you tell me more about the latest DeFi developments?",
        "What are the implications of the new regulatory framework?",
        "How will this affect the price of Bitcoin?"
      ];
      
      const randomText = mockTexts[Math.floor(Math.random() * mockTexts.length)];
      setRecordingText(randomText);
    }, 2000);
  };
  
  const stopRecording = () => {
    setIsRecording(false);
    if (recordingText) {
      onRecordingComplete(recordingText);
    }
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' + secs : secs}`;
  };
  
  return (
    <div className="voice-recorder">
      {isRecording ? (
        <>
          <div className="recording-animation">
            <div className="recording-indicator"></div>
            <span className="recording-time">{formatTime(recordingTime)}</span>
          </div>
          
          {recordingText && (
            <div className="recognized-text">
              "{recordingText}"
            </div>
          )}
          
          <button 
            className="record-button stop"
            onClick={stopRecording}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>
            </svg>
            Stop Recording
          </button>
        </>
      ) : (
        <button 
          className="record-button"
          onClick={startRecording}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
          Record Question
        </button>
      )}
    </div>
  );
}

export default VoiceRecorder;