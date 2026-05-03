import React, { memo } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const timelineData = [
  {
    id: 'register',
    en: { title: '1. Register to Vote', desc: 'Check your eligibility and register before the deadline. You can usually do this online, by mail, or in-person.' },
    te: { title: '1. ఓటు వేయడానికి నమోదు చేసుకోండి', desc: 'మీ అర్హతను తనిఖీ చేయండి మరియు గడువుకు ముందే నమోదు చేసుకోండి. మీరు సాధారణంగా దీన్ని ఆన్‌లైన్‌లో, మెయిల్ ద్వారా లేదా వ్యక్తిగతంగా చేయవచ్చు.' }
  },
  {
    id: 'research',
    en: { title: '2. Research Candidates', desc: 'Look past the ads! Read candidate platforms, watch townhalls, and identify who aligns with your core values.' },
    te: { title: '2. అభ్యర్థులను పరిశోధించండి', desc: 'ప్రకటనలను పక్కన పెట్టండి! అభ్యర్థి ప్లాట్‌ఫారమ్‌లను చదవండి, టౌన్‌హాల్స్‌ను చూడండి మరియు మీ ప్రధాన విలువలకు ఎవరు సరిపోలుతారో గుర్తించండి.' }
  },
  {
    id: 'vote',
    en: { title: '3. Cast Your Ballot', desc: 'Find your polling place or request an absentee ballot. Make sure you bring required ID if your state mandates it.' },
    te: { title: '3. మీ ఓటు వేయండి', desc: 'మీ పోలింగ్ స్థలాన్ని కనుగొనండి లేదా హాజరుకాని బ్యాలెట్‌ను అభ్యర్థించండి. మీ రాష్ట్రం ఆదేశిస్తే అవసరమైన IDని తీసుకురావాలని నిర్ధారించుకోండి.' }
  }
];

const JourneyTimeline = memo(() => {
  const { language } = useLanguage();

  return (
    <div className="glass-panel" style={{ marginTop: '24px' }}>
      <h2 style={{ marginBottom: '24px', color: 'var(--accent-cyan)' }}>
        {language === 'en' ? 'The Voter\'s Journey' : 'ఓటరు ప్రయాణం'}
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', position: 'relative', paddingLeft: '24px', borderLeft: '2px solid var(--border-glass)' }}>
        {timelineData.map((step) => (
          <div key={step.id} style={{ position: 'relative' }}>
            <div style={{
              position: 'absolute',
              left: '-33px',
              top: '4px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: 'var(--accent-magenta)',
              boxShadow: '0 0 10px var(--accent-magenta)'
            }} />
            <h3 style={{ marginBottom: '8px' }}>{step[language].title}</h3>
            <p style={{ color: 'var(--text-secondary)' }}>{step[language].desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
});

export default JourneyTimeline;
