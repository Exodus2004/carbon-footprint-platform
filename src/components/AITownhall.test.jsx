import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import AITownhall from './AITownhall';
import { LanguageProvider } from '../contexts/LanguageContext';

describe('AITownhall Component', () => {
  it('renders the component with the correct title', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    
    // Check if the main title is present
    expect(screen.getByText('AI Townhall Simulator')).toBeDefined();
  });

  it('renders the input field and simulate button', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    
    // Check if the input field is present by placeholder or aria-label
    const input = screen.getByPlaceholderText('e.g., Universal Healthcare, Carbon Tax...');
    expect(input).toBeDefined();

    // Check if the simulate button is present
    const button = screen.getByRole('button', { name: /simulate debate/i });
    expect(button).toBeDefined();
  });
});
