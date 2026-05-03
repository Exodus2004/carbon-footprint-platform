import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AITownhall from './AITownhall';
import { LanguageProvider } from '../contexts/LanguageContext';

// Mock the GoogleGenAI module
vi.mock('@google/genai', () => {
  return {
    GoogleGenAI: vi.fn().mockImplementation(() => ({
      models: {
        generateContent: vi.fn().mockResolvedValue({
          text: 'Mocked debate response: Both candidates make good points.',
        }),
      },
    })),
  };
});

describe('AITownhall Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  it('renders the component with the correct title', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    expect(screen.getByText('AI Townhall Simulator')).toBeDefined();
  });

  it('renders the input field and simulate button', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    const input = screen.getByPlaceholderText('e.g., Universal Healthcare, Carbon Tax...');
    expect(input).toBeDefined();

    const button = screen.getByRole('button', { name: /simulate debate/i });
    expect(button).toBeDefined();
  });

  it('updates the input field when the user types', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    const input = screen.getByPlaceholderText('e.g., Universal Healthcare, Carbon Tax...');
    
    // Type into the input
    fireEvent.change(input, { target: { value: 'Universal Healthcare' } });
    
    // Check if value updated
    expect(input.value).toBe('Universal Healthcare');
  });

  it('has disabled button initially and enables when input has text', () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    
    const button = screen.getByRole('button', { name: /simulate debate/i });
    expect(button.disabled).toBe(true);

    const input = screen.getByPlaceholderText('e.g., Universal Healthcare, Carbon Tax...');
    fireEvent.change(input, { target: { value: 'Education Reform' } });
    
    expect(button.disabled).toBe(false);
  });

  it('displays the result from the API after simulation', async () => {
    render(
      <LanguageProvider>
        <AITownhall />
      </LanguageProvider>
    );
    
    const input = screen.getByPlaceholderText('e.g., Universal Healthcare, Carbon Tax...');
    fireEvent.change(input, { target: { value: 'AI Regulation' } });

    const button = screen.getByRole('button', { name: /simulate debate/i });
    fireEvent.click(button);

    // Wait for the mocked response to be rendered
    await waitFor(() => {
      expect(screen.getByTestId('debate-output')).toBeDefined();
    });
    
    expect(screen.getByText('Mocked debate response: Both candidates make good points.')).toBeDefined();
  });
});
