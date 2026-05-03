import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const Navbar = ({ activeTab, setActiveTab }) => {
  const { t, toggleLanguage, language } = useLanguage();

  return (
    <header className="header" style={{ position: 'sticky', top: 0, zIndex: 100, background: 'rgba(5, 5, 5, 0.8)', backdropFilter: 'blur(10px)' }}>
      <div className="logo">{t('appTitle')}</div>
      <nav style={{ display: 'flex', gap: '16px' }}>
        <button 
          className={activeTab === 'journey' ? 'btn-primary' : 'btn-outline'} 
          onClick={() => setActiveTab('journey')}
          style={{ padding: '8px 16px', fontSize: '0.9rem' }}
        >
          {t('journeyNav')}
        </button>
        <button 
          className={activeTab === 'townhall' ? 'btn-primary' : 'btn-outline'} 
          onClick={() => setActiveTab('townhall')}
          style={{ padding: '8px 16px', fontSize: '0.9rem' }}
        >
          {t('townhallNav')}
        </button>
        <button 
          className={activeTab === 'quiz' ? 'btn-primary' : 'btn-outline'} 
          onClick={() => setActiveTab('quiz')}
          style={{ padding: '8px 16px', fontSize: '0.9rem' }}
        >
          {t('quizNav')}
        </button>
      </nav>
      <button className="btn-outline" onClick={toggleLanguage}>
        {t('toggleLanguage')}
      </button>
    </header>
  );
};

export default Navbar;
