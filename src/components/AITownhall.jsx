import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { GoogleGenAI } from '@google/genai';

// Initialize the API (Requires VITE_GEMINI_API_KEY in .env)
const apiKey = import.meta.env.VITE_GEMINI_API_KEY || '';
const ai = new GoogleGenAI({ apiKey: apiKey });

const AITownhall = () => {
  const { language } = useLanguage();
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [debateOutput, setDebateOutput] = useState('');

  const strings = {
    en: {
      title: 'AI Townhall Simulator',
      desc: 'Enter a controversial topic, and our AI will simulate a townhall debate between two differing viewpoints to help you analyze political rhetoric.',
      placeholder: 'e.g., Universal Healthcare, Carbon Tax...',
      button: 'Simulate Debate',
      error: 'Please enter a valid API key in your .env file.',
      analyzing: 'Analyzing rhetoric and generating debate...'
    },
    te: {
      title: 'AI టౌన్‌హాల్ సిమ్యులేటర్',
      desc: 'ఒక వివాదాస్పద అంశాన్ని నమోదు చేయండి మరియు రాజకీయ ప్రసంగాన్ని విశ్లేషించడంలో మీకు సహాయపడటానికి మా AI రెండు భిన్నమైన దృక్కోణాల మధ్య టౌన్‌హాల్ చర్చను అనుకరిస్తుంది.',
      placeholder: 'ఉదా., యూనివర్సల్ హెల్త్‌కేర్, కార్బన్ టాక్స్...',
      button: 'చర్చను అనుకరించండి',
      error: 'దయచేసి మీ .env ఫైల్‌లో చెల్లుబాటు అయ్యే API కీని నమోదు చేయండి.',
      analyzing: 'ప్రసంగాన్ని విశ్లేషించడం మరియు చర్చను రూపొందించడం...'
    }
  };

  const t = strings[language];

  const handleSimulate = async () => {
    if (!topic.trim()) return;
    if (!apiKey) {
      setDebateOutput(t.error);
      return;
    }

    setLoading(true);
    setDebateOutput('');

    try {
      // Prompt Engineering for Google Prompt Wars
      const prompt = `You are an expert political analyst. Simulate a short townhall debate about "${topic}". 
      Present two distinct personas (Candidate A and Candidate B) debating the topic.
      Then, provide a brief non-partisan analysis of the rhetorical strategies they used.
      IMPORTANT: Your entire response MUST be in ${language === 'en' ? 'English' : 'Telugu'}.`;

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
      });

      setDebateOutput(response.text);
    } catch (error) {
      console.error(error);
      setDebateOutput('Error generating debate. Please check API key and console.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ marginTop: '24px' }}>
      <h2 style={{ marginBottom: '16px', color: 'var(--accent-magenta)' }}>{t.title}</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>{t.desc}</p>
      
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <input 
          type="text" 
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder={t.placeholder}
          style={{
            flex: 1,
            padding: '12px 16px',
            borderRadius: '8px',
            border: '1px solid var(--border-glass)',
            background: 'rgba(255, 255, 255, 0.05)',
            color: 'var(--text-primary)',
            fontSize: '1rem',
            outline: 'none'
          }}
        />
        <button 
          className="btn-primary" 
          onClick={handleSimulate}
          disabled={loading || !topic.trim()}
          style={{ opacity: loading || !topic.trim() ? 0.7 : 1 }}
        >
          {loading ? t.analyzing : t.button}
        </button>
      </div>

      {debateOutput && (
        <div style={{ 
          padding: '24px', 
          background: 'rgba(0,0,0,0.3)', 
          borderRadius: '8px', 
          whiteSpace: 'pre-wrap',
          lineHeight: '1.8'
        }}>
          {debateOutput}
        </div>
      )}
    </div>
  );
};

export default AITownhall;
