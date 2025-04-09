import React, { useState, useEffect, useRef } from 'react';
import SearchBar from '../components/SearchBar';
import LoadingIndicator from '../components/LoadingIndicator';
import TwitterFeed from '../components/TwitterFeed';
import VoiceRecorder from '../components/VoiceRecorder';
import Krakbit from '../components/Krakbit';
import '../styles/HomePage.css';
import { io } from "socket.io-client"
// src/pages/HomePage.js

// textToSpeech.js

function HomePage() {

  const socketRef = useRef(null);

  const [newsArticles, setNewsArticles] = useState([]);
  const [xArticles, setXArticles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const [questionResponse, setQuestionResponse] = useState('');
  const inputRef = useRef();
  const qRef = useRef();

  const askQuestion = () => {
    let question = inputRef.current.value;
    let context = newsArticles.map(article => article.content).join(" ");

    fetch('http://localhost:8000/ask_question', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question,
        content: context
      }),
    })
      .then(res => res.json())
      .then(data => {
        console.log('Response:', data);
        setQuestionResponse(data.response);
      })
      .catch(err => {
        console.error('Error:', err);
      });
  }


  useEffect(() => {
    socketRef.current = io("http://localhost:8000");
  
    socketRef.current.on("connect", () => {
      console.log("Connected to WebSocket server");
    });
  
    socketRef.current.on("client_comms", (data) => {
      const type = data.data.type;
  
      if (type === "status") {
        setLoadingStatus(data.data.status);
        console.log("New Status", data.data.status);
      }
  
      if (type === "new_data") {
        setIsLoading(false);
        const new_article = data.data.info;
        setNewsArticles((prevArticles) => [...prevArticles, new_article]);
        console.log("New Article", new_article);
      }
  
      if (type === "new_data_x") {
        setIsLoading(false);
        const new_article = data.data.info;
        setXArticles(new_article);
        console.log("New Articles (X)", new_article);
      }
    });
  
    socketRef.current.on("disconnect", () => {
      console.log("Disconnected from WebSocket server");
    });

    fetch('http://localhost:8000/get_x_trending').then(res => res.json()).then(data => {
      console.log("GOT X DATA")
      console.log(data)
      setXArticles(data.posts)
    })
  
    return () => {
      socketRef.current.disconnect();
    };
  }, []);


  const generateDailyKrakbit = () => {
    setIsLoading(true);
    setNewsArticles([]);
  
    if (socketRef.current) {
      socketRef.current.emit("gen_daily");
    } else {
      console.warn("WebSocket not connected yet.");
    }
  };

  const handleQ = (question) => {

    setIsLoading(true);
    setNewsArticles([]);
    
    if (socketRef.current) {
      socketRef.current.emit("gen_question", { query: question });
    } else {
      console.warn("WebSocket not connected yet.");
    }
  }


  return (
    <div className="home-container">
      <section className="hero-section">
        <h1>Decentralized News For The Digital Age</h1>
        <p>Blockchain-verified news and insights delivered daily</p>
        <SearchBar innerQ={handleQ}/>
      </section>

      <section className="daily-section">
        <div className="daily-header">
          <h2>Krakbits</h2>
          <button
            className="generate-btn"
            onClick={generateDailyKrakbit}
            disabled={isLoading}
          >
            Generate Daily Krakbit
          </button>
        </div>
        {
          !isLoading && newsArticles.length === 0 && (
          <p>Click the button above to generate your daily news digest, or ask a question to create a personalized Krakbit!</p>
        )
        }

        {isLoading ? (
          <LoadingIndicator status={loadingStatus} />
        ) : (
          newsArticles.length > 0 && <Krakbit articles={newsArticles} />
        )}

        {newsArticles.length > 0 && (
          <div className="voice-interaction">
            <button
              className="voice-btn"
              onClick={() => setShowVoiceRecorder(!showVoiceRecorder)}
            >
              {showVoiceRecorder ? 'Cancel' : 'Ask Follow-up Question'}
            </button>
            {showVoiceRecorder && (
             <div>

              <input style={{
                width: '500px',
                marginTop: '15px'
              }} ref={inputRef}></input>
              <button style={{marginLeft: '5px'}} onClick={askQuestion}>
                Submit
              </button>

                <VoiceRecorder
                onRecordingComplete={(text) => {
                  console.log('Voice question:', text);
                  setShowVoiceRecorder(false);
                }}
              />

             </div>
            )}

            {questionResponse && questionResponse.length > 0 &&
            <p style={{
              marginTop: '15px',
              border: '1px solid lightgray',
              padding: '10px',
              borderRadius: '5px',
              backgroundColor: '#f9f9f9',
              color: '#333',
              fontFamily: 'Arial, sans-serif',
              fontSize: '16px',
              lineHeight: '1.5',
              fontWeight: 'normal',
              textAlign: 'left',
              textTransform: 'none',
              textDecoration: 'none',
              whiteSpace: 'pre-wrap',
            }}>
              {questionResponse}

            </p>}
          </div>
        )}
      </section>

      <section className="social-feed" style={{ marginTop: '30px' }}>
        <h2>Trending & Latest on X</h2>
        {xArticles.length > 0 ? <TwitterFeed articles={xArticles} />  : <LoadingIndicator status={true} />}
      </section>
    </div>
  );
}

export default HomePage;