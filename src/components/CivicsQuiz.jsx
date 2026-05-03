import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const questions = [
  {
    en: { q: 'Which level of government handles most election administration?', options: ['Federal', 'State', 'County/Local', 'International'], a: 2 },
    te: { q: 'ఏ స్థాయి ప్రభుత్వం ఎక్కువగా ఎన్నికల పరిపాలనను నిర్వహిస్తుంది?', options: ['ఫెడరల్ (కేంద్ర)', 'రాష్ట్ర', 'కౌంటీ/స్థానిక', 'అంతర్జాతీయ'], a: 2 }
  },
  {
    en: { q: 'What is a primary election?', options: ['The final election for office', 'An election to choose a party\'s candidate', 'A local bond measure', 'A recount'], a: 1 },
    te: { q: 'ప్రైమరీ ఎన్నికలు అంటే ఏమిటి?', options: ['పదవికి తుది ఎన్నికలు', 'పార్టీ అభ్యర్థిని ఎంచుకోవడానికి ఎన్నికలు', 'స్థానిక బాండ్ కొలత', 'రీకౌంట్'], a: 1 }
  }
];

const CivicsQuiz = () => {
  const { language } = useLanguage();
  const [currentQ, setCurrentQ] = useState(0);
  const [score, setScore] = useState(0);
  const [showScore, setShowScore] = useState(false);

  const t = {
    en: { title: 'Civics Quiz', scoreText: 'You scored {score} out of {total}', restart: 'Restart Quiz' },
    te: { title: 'సివిక్స్ క్విజ్', scoreText: 'మీరు {total} కి గాను {score} సాధించారు', restart: 'క్విజ్‌ని పునఃప్రారంభించండి' }
  }[language];

  const handleAnswer = (index) => {
    if (index === questions[currentQ][language].a) {
      setScore(score + 1);
    }
    const nextQ = currentQ + 1;
    if (nextQ < questions.length) {
      setCurrentQ(nextQ);
    } else {
      setShowScore(true);
    }
  };

  const restartQuiz = () => {
    setScore(0);
    setCurrentQ(0);
    setShowScore(false);
  };

  return (
    <div className="glass-panel" style={{ marginTop: '24px' }}>
      <h2 style={{ marginBottom: '24px', color: 'var(--accent-cyan)' }}>{t.title}</h2>
      
      {showScore ? (
        <div style={{ textAlign: 'center', padding: '32px' }}>
          <h3 style={{ fontSize: '2rem', marginBottom: '16px' }}>
            {t.scoreText.replace('{score}', score).replace('{total}', questions.length)}
          </h3>
          <button className="btn-primary" onClick={restartQuiz}>{t.restart}</button>
        </div>
      ) : (
        <div>
          <h3 style={{ marginBottom: '24px', fontSize: '1.2rem' }}>
            {currentQ + 1}. {questions[currentQ][language].q}
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {questions[currentQ][language].options.map((option, index) => (
              <button 
                key={index} 
                className="btn-outline" 
                style={{ textAlign: 'left', padding: '16px', fontSize: '1rem' }}
                onClick={() => handleAnswer(index)}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CivicsQuiz;
