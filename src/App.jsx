import React, { useState, Suspense, lazy } from 'react'
import './App.css'
import { useLanguage } from './contexts/LanguageContext'
import Navbar from './components/Navbar'
import JourneyTimeline from './components/JourneyTimeline'
import CivicsQuiz from './components/CivicsQuiz'

// Lazy load the AITownhall component for performance efficiency
const AITownhall = lazy(() => import('./components/AITownhall'));

function App() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'home' && (
          <section className="glass-panel text-center" style={{ textAlign: 'center', padding: '48px 24px' }}>
            <h1 style={{ marginBottom: '16px', fontSize: '2.5rem', color: 'var(--accent-cyan)' }}>
              {t('welcomeTitle')}
            </h1>
            <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '32px' }}>
              {t('welcomeSubtitle')}
            </p>
            <button className="btn-primary" style={{ fontSize: '1.1rem' }} onClick={() => setActiveTab('journey')} aria-label={t('getStarted')}>
              {t('getStarted')}
            </button>
          </section>
        )}

        {activeTab === 'journey' && <JourneyTimeline />}
        {activeTab === 'quiz' && <CivicsQuiz />}
        {activeTab === 'townhall' && (
          <Suspense fallback={<div className="glass-panel" style={{ marginTop: '24px', textAlign: 'center', color: 'var(--accent-cyan)' }}>Loading AI Townhall...</div>}>
            <AITownhall />
          </Suspense>
        )}
      </main>
    </div>
  )
}

export default App
