import React, { createContext, useState, useContext } from 'react';

// Basic Dictionary for Demo Purposes
const dictionary = {
  en: {
    appTitle: "Democracyverse",
    toggleLanguage: "Switch to Telugu",
    welcomeTitle: "Welcome to Democracyverse",
    welcomeSubtitle: "Your interactive guide to the election process.",
    getStarted: "Get Started",
    townhallNav: "AI Townhall",
    journeyNav: "Voter Journey",
    quizNav: "Civics Quiz"
  },
  te: {
    appTitle: "డెమోక్రసీవర్స్",
    toggleLanguage: "English లోకి మార్చండి",
    welcomeTitle: "డెమోక్రసీవర్స్ కు స్వాగతం",
    welcomeSubtitle: "ఎన్నికల ప్రక్రియకు మీ ఇంటరాక్టివ్ గైడ్.",
    getStarted: "ప్రారంభించండి",
    townhallNav: "AI టౌన్ హాల్",
    journeyNav: "ఓటరు ప్రయాణం",
    quizNav: "సివిక్స్ క్విజ్"
  }
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');

  const toggleLanguage = () => {
    setLanguage((prevLang) => (prevLang === 'en' ? 'te' : 'en'));
  };

  const t = (key) => {
    return dictionary[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
