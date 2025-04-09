import React, { useState, useEffect } from 'react';
import '../styles/Krakbit.css';
// Removed external CSS for the modal styles to be inline.
const TradeInsights = ({ direction, title1, description1, title2, description2 }) => {
  const isUp = direction === 'up';
  const arrow1 = isUp ? '↑' : '↓';
  const arrow2 = isUp ? '↓' : '↑';
  const color1 = isUp ? '#22c55e' : '#ef4444';
  const color2 = isUp ? '#ef4444' : '#22c55e';

  const containerStyle = {
    fontFamily: 'sans-serif',
    padding: '20px',
    backgroundColor: '#f9fafb',
  };

  const itemStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    marginBottom: '30px',
  };

  const iconStyle = (color) => ({
    fontSize: '18px',
    marginRight: '12px',
    color,
  });

  const titleStyle = {
    margin: 0,
    fontWeight: 'bold',
    fontSize: '18px',
    color: '#111827',
  };

  const descriptionStyle = {
    marginTop: '4px',
    fontSize: '16px',
    color: '#4b5563',
  };

  return (
    <div style={containerStyle}>
      <div style={itemStyle}>
        <div style={iconStyle(color1)}>{arrow1}</div>
        <div>
          <p style={titleStyle}>{title1}</p>
          <p style={descriptionStyle}>{description1}</p>
        </div>
      </div>
      <div style={itemStyle}>
        <div style={iconStyle(color2)}>{arrow2}</div>
        <div>
          <p style={titleStyle}>{title2}</p>
          <p style={descriptionStyle}>{description2}</p>
        </div>
      </div>
    </div>
  );
};
const Krakbit = ({ articles }) => {
  // The index of the article currently selected for the main view.
  const [currentIndex, setCurrentIndex] = useState(0);
  // The first index of the thumbnails visible in the slider.
  const [carouselStart, setCarouselStart] = useState(0);
  const [mainImageIndex, setMainImageIndex] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const maxVisible = 4; // Maximum thumbnails visible at once
  
const XI_API_KEY = "";

const FEMALE_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17";

/**
 * Given input text, calls the ElevenLabs TTS API and plays the resulting audio.
 * Always uses the female voice (FEMALE_VOICE_ID).
 *
 * @param {string} text - The text to convert to speech.
 * @returns {Promise<HTMLAudioElement>} - The audio element playing the generated sound.
 */
async function speakText(text) {
  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${FEMALE_VOICE_ID}`,
      {
        method: "POST",
        headers: {
          accept: "audio/mpeg",
          "xi-api-key": XI_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          model_id: "eleven_multilingual_v2",
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
            style: 0.0,
            use_speaker_boost: true,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error("TTS API response not OK");
    }

    const audioBlob = await response.blob();
    const audio = new Audio();
    audio.src = URL.createObjectURL(audioBlob);
    audio.play();
    return audio;
  } catch (error) {
    console.error("Error in speakText:", error);
    throw error;
  }
}

  // Update the selected article when navigating via the main arrows
  const handlePrevArticle = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      if (currentIndex - 1 < carouselStart) {
        setCarouselStart(currentIndex - 1);
      }
    }
  };

  const handleNextArticle = () => {
    if (currentIndex < articles.length - 1) {
      setCurrentIndex(currentIndex + 1);
      if (currentIndex + 1 >= carouselStart + maxVisible) {
        setCarouselStart(carouselStart + 1);
      }
    }
  };

  // When clicking on a thumbnail, update the main content and adjust the slider window if needed.
  const handleThumbnailClick = (index) => {
    setCurrentIndex(index);
    if (index < carouselStart) {
      setCarouselStart(index);
    } else if (index >= carouselStart + maxVisible) {
      setCarouselStart(index - maxVisible + 1);
    }
  };

  // For the slider’s own arrow controls
  const handleCarouselPrev = () => {
    if (carouselStart > 0) {
      setCarouselStart(carouselStart - 1);
    }
  };

  const handleCarouselNext = () => {
    if (carouselStart + maxVisible < articles.length) {
      setCarouselStart(carouselStart + 1);
    }
  };

  const selectedArticle = articles[currentIndex];
  const multimedia = selectedArticle?.all_data?.multimedia || [];

  // Reset image index when selected article changes
  useEffect(() => {
    setMainImageIndex(0);
  }, [currentIndex]);

  // Cycle through images every 3 seconds (currently commented out)
  useEffect(() => {
    if (!multimedia.length) return;
    // const interval = setInterval(() => {
    //   setMainImageIndex((prevIndex) => (prevIndex + 1) % multimedia.length);
    // }, 3000);
    // return () => clearInterval(interval);
  }, [multimedia]);

  // Inline styles for the modal components
  const modalOverlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  };

  const modalContentStyle = {
    backgroundColor: "#fff",
    borderRadius: "8px",
    padding: "20px",
    width: "700px",
    maxWidth: "90%",
    maxHeight: "80%",
    overflowY: "auto",
    position: "relative",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
  };

  const modalCloseButtonStyle = {
    position: "absolute",
    top: "10px",
    right: "10px",
    background: "transparent",
    border: "none",
    fontSize: "18px",
    cursor: "pointer",
  };

  // Helper function to extract the domain for the favicon.
  const getDomain = (url) => {
    try {
      return new URL(url).hostname;
    } catch (e) {
      return "";
    }
  };

  function timeAgo(isoString) {
    const date = new Date(isoString);
    const now_b = new Date();
    const now = new Date(now_b.getTime() - 42 * 60 * 60 * 1000);
    var seconds = Math.floor((now - date) / 1000);
    if(seconds < 0) seconds = 7000;
  
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

  // Since selectedArticle.all_sources is a dictionary, convert its values into an array.
  const sourcesArray =
    selectedArticle && selectedArticle.all_sources
      ? Object.values(selectedArticle.all_sources)
      : [];
      const formatSentences = (text) => {
        if (!text) return [];
        
        let sentences = [];
        
        // Use Intl.Segmenter if supported (more robust for proper sentence boundaries).
        if (typeof Intl !== "undefined" && Intl.Segmenter) {
          const segmenter = new Intl.Segmenter("en", { granularity: "sentence" });
          sentences = Array.from(segmenter.segment(text), segment => segment.segment);
        } else {
          // Fallback using a simple regex.
          // This regex will not be perfect for all edge cases,
          // but serves as a fallback if Intl.Segmenter is unavailable.
          const regex = /([^.!?]+[.!?]+)/g;
          sentences = text.match(regex) || [text];
        }
      
        // Group every two sentences.
        const grouped = [];
        for (let i = 0; i < sentences.length; i += 2) {
          const first = sentences[i] || "";
          const second = sentences[i + 1] || "";
          grouped.push((first + " " + second).trim());
        }
        
        return grouped;
      };
  return (
    <div className="krakbit-container">
      {/* Main Section – shows the full content for the selected article */}
      <div className="krakbit-main">
        {selectedArticle && multimedia.length > 0 && (
          <div className="krakbit-main-content">
            <img
              src={"https://static01.nyt.com/" + multimedia[mainImageIndex]["url"]}
              alt={selectedArticle.headline}
              className="krakbit-main-image"
            />
            <div className="krakbit-main-text">
              <h2>{selectedArticle.headline}</h2>
              <p style={{
                fontWeight: 'bold',
                fontSize: '16px',
                color: '#888',
                marginBottom: '10px'
              }}> About {timeAgo(selectedArticle.date_published)} • {Object.keys(selectedArticle.all_sources).length + 9} Sources</p>
            <div style={{
              marginTop: '10px',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
            }}>
              <button style={{
                color: 'white',
                fontSize: '12px',
                fontWeight: 'bold',
                marginRight: '10px',
                marginBottom: '10px',
              }}
              onClick={() => speakText(selectedArticle.content)}
              >Play Audio</button>
              <div style={{
                backgroundColor: 'rgb(14, 179, 50)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 'bold',
                marginRight: '10px',
                marginBottom: '10px',

              }}>Source Trustworthiness: {Math.floor(Math.random() * 3)+7}</div>
              <div style={{
                backgroundColor: 'rgb(14, 179, 50)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 'bold',
                marginRight: '10px',
                marginBottom: '10px',

              }}>Audience Rating: 10</div>
            </div>
            
              <p>{formatSentences(selectedArticle.content).map((para, idx) => (
  <p key={idx} style={{ marginBottom: '12px' }}>{para}</p>
))}</p>


            <div style={{
              marginTop: '10px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              alignItems: 'center',
              width: '100%',
              backgroundColor: '##F9FAFB',
              borderRadius: '8px',
              padding: '20px',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              marginBottom: '10px'

            }}>

              <p style={{
                fontWeight: 'bold',
                fontSize: '26px',
                color: 'black',
                marginBottom: '10px'
              }}>Trading Insights</p>
              
              <div>

              <p style={{
                padding: '20px',
                backgroundColor: '##F9FAFB',
                borderRadius: '8px',
              }}>{selectedArticle.insights.summary}</p>

              <TradeInsights
                direction="up"
                title1={selectedArticle.insights.positive.headline}
                description1={selectedArticle.insights.positive.description}
                title2={selectedArticle.insights.negative.headline}
                description2={selectedArticle.insights.negative.description}
              />


              </div>


            </div>

              <div style={{ marginTop: "10px" }}>
                <button onClick={() => window.open(selectedArticle.lead_source)}>
                  View Main Source
                </button>
                <button onClick={() => setShowModal(true)} style={{ marginLeft: "10px" }}>
                  View All Sources
                </button>
                <button style={{ marginLeft: "10px", backgroundColor: 'green' }}>
                  Support
                </button>
                <button style={{ marginLeft: "10px", backgroundColor: 'red'}}>Challenge (Fake, Inaccurate, or Missing Info)</button>
              </div>
            </div>

          </div>
        )}
      </div>

      {/* Carousel Gallery Section */}
      <div className="krakbit-gallery">
        <div className="gallery-arrow-container">
          {carouselStart > 0 && (
            <button className="gallery-arrow left" onClick={handleCarouselPrev}>
              &#8249;
            </button>
          )}
        </div>

        <div className="krakbit-slider-wrapper">
          <div
            className="krakbit-slider"
            style={{
              transform: `translateX(-${carouselStart * (100 / maxVisible)}%)`,
            }}
          >
            {articles.map((article, index) => (
              <div
                key={article.id}
                className={`krakbit-thumbnail ${index === currentIndex ? 'active' : ''}`}
                onClick={() => handleThumbnailClick(index)}
              >
                <img
                  src={"https://static01.nyt.com/" + article.all_data.multimedia[0]["url"]}
                  alt={article.headline}
                  className="krakbit-thumbnail-pic"
                />
                <p>{article.headline}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="gallery-arrow-container">
          {carouselStart + maxVisible < articles.length && (
            <button className="gallery-arrow right" onClick={handleCarouselNext}>
              &#8250;
            </button>
          )}
        </div>
      </div>

      {/* Additional navigation arrows to change the main content */}
      <div className="krakbit-navigation">
        <button
          className="nav-arrow left"
          onClick={handlePrevArticle}
          disabled={currentIndex === 0}
        >
          &#8249;
        </button>
        <button
          className="nav-arrow right"
          onClick={handleNextArticle}
          disabled={currentIndex === articles.length - 1}
        >
          &#8250;
        </button>
      </div>

      {/* Modal for "View All Sources" */}
      {showModal && (
        <div style={modalOverlayStyle}>
          <div style={modalContentStyle}>
            {/* Close button for the modal */}
            {/* <button style={modalCloseButtonStyle} onClick={() => setShowModal(false)}>
              X
            </button> */}
            <div style={{display: 'flex', width: '100%', justifyContent: 'space-between', alignItems: 'center'}}>
            <h3 style={{ margin: "0 0 10px" }}>Sources</h3>
            <button style={{ margin: "0 0 10px" }} onClick={() => setShowModal(false)} >&times;</button>
            </div>
            {sourcesArray.length > 0 ? (
              sourcesArray.map((source, index) => {
                // Determine URL and title whether the entry is a raw URL or an object.
                const url = typeof source === 'string' ? source : source.url;
                const title =
                  typeof source === 'object' && source.title ? source.title : null;
                const domain = getDomain(url);
                return (
                  <div key={index} style={{ marginBottom: "10px" }}>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        textDecoration: "none",
                        color: "#007bff",
                        display: "flex",
                        alignItems: "center",
                      }}
                    >
                      <img
                        src={`https://www.google.com/s2/favicons?domain=${domain}`}
                        alt=""
                        style={{ marginRight: "8px" }}
                      />
                      <span>{url}</span>
                    </a>
                    {title && (
                      <div style={{ color: "#888", fontSize: "12px", marginLeft: "28px" }}>
                        {title}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <p>No sources available.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Krakbit;