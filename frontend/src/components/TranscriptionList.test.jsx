import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TranscriptionList from './TranscriptionList';

// Mock fetch globally
global.fetch = jest.fn();

// Mock the SVG imports
jest.mock('../assets/match-case.svg', () => 'match-case-icon');
jest.mock('../assets/match_full_file_name.svg', () => 'full-file-icon');

describe('TranscriptionList', () => {
    const mockTranscriptions = [
        {
            id: 1,
            original_audio_filename: 'test1.m4a',
            created_at: '2023-01-01T12:00:00Z',
            text: 'This is test transcription 1',
            audio_filepath: '/audio/test1.m4a'
        },
        {
            id: 2,
            original_audio_filename: 'test2.m4a',
            created_at: '2023-01-02T12:00:00Z',
            text: 'This is test transcription 2',
            audio_filepath: '/audio/test2.m4a'
        }
    ];

    beforeEach(() => {
        // Reset all mocks before each test
        jest.clearAllMocks();
        
        // Mock successful fetch response for initial load
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockTranscriptions
        });
    });

    test('renders the component with title', async () => {
        await act(async () => {
            render(<TranscriptionList />);
        });

        expect(screen.getByText('Past Transcriptions')).toBeInTheDocument();
        expect(screen.getByText('Transcriptions')).toBeInTheDocument();
    });

    test('fetches and displays transcriptions on initial load', async () => {
        await act(async () => {
            render(<TranscriptionList />);
        });

        // Check that the fetch was called with the correct URL
        expect(global.fetch).toHaveBeenCalledWith('http://localhost:9090/api/transcriptions');
        
        // Check that the transcriptions are displayed
        await waitFor(() => {
            expect(screen.getByText('test1.m4a')).toBeInTheDocument();
            expect(screen.getByText('test2.m4a')).toBeInTheDocument();
            expect(screen.getByText('This is test transcription 1')).toBeInTheDocument();
            expect(screen.getByText('This is test transcription 2')).toBeInTheDocument();
        });
    });

    test('handles search functionality', async () => {
        // First render with initial data
        await act(async () => {
            render(<TranscriptionList />);
        });

        // Mock the search response
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => [mockTranscriptions[0]] // Only return the first item for the search
        });

        // Enter search term
        const searchInput = screen.getByPlaceholderText('Search by audio file name');
        fireEvent.change(searchInput, { target: { value: 'test1' } });
        
        // Click search button
        const searchButton = screen.getByText('Search');
        await act(async () => {
            fireEvent.click(searchButton);
        });

        // Check that the fetch was called with the correct search parameters
        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:9090/api/search?file_name=test1&match_full_file_name=false&match_case=false'
        );
        
        // Verify the search results
        await waitFor(() => {
            expect(screen.getByText('test1.m4a')).toBeInTheDocument();
            expect(screen.queryByText('test2.m4a')).not.toBeInTheDocument();
        });
    });

    test('handles search with match case and full file name toggles', async () => {
        // First render with initial data
        await act(async () => {
            render(<TranscriptionList />);
        });

        // Mock the search response
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => [mockTranscriptions[0]]
        });

        // Enter search term
        const searchInput = screen.getByPlaceholderText('Search by audio file name');
        fireEvent.change(searchInput, { target: { value: 'test1' } });
        
        // Toggle match case and full file name
        const matchCaseImg = screen.getByAltText('Match Case');
        const fullFileNameImg = screen.getByAltText('Match Full File Name');
        
        fireEvent.click(matchCaseImg);
        fireEvent.click(fullFileNameImg);
        
        // Press Enter to search
        await act(async () => {
            fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' });
        });

        // Check that the fetch was called with the correct search parameters
        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:9090/api/search?file_name=test1&match_full_file_name=true&match_case=true'
        );
    });

    test('handles clear search functionality', async () => {
        // First render with initial data
        await act(async () => {
            render(<TranscriptionList />);
        });

        // Enter search term
        const searchInput = screen.getByPlaceholderText('Search by audio file name');
        fireEvent.change(searchInput, { target: { value: 'test1' } });
        
        // Toggle match case and full file name
        const matchCaseImg = screen.getByAltText('Match Case');
        const fullFileNameImg = screen.getByAltText('Match Full File Name');
        
        fireEvent.click(matchCaseImg);
        fireEvent.click(fullFileNameImg);
        
        // Clear fetch mock to track new calls
        global.fetch.mockClear();
        
        // Mock the response for fetchTranscriptions after clear
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockTranscriptions
        });

        // Click clear search
        const clearButton = screen.getByText('Clear Search');
        await act(async () => {
            fireEvent.click(clearButton);
        });

        // Check that the input was cleared
        expect(searchInput.value).toBe('');
        
        // Check that fetchTranscriptions was called
        expect(global.fetch).toHaveBeenCalledWith('http://localhost:9090/api/transcriptions');
    });

    test('clears search when clearSearchContent event is dispatched', async () => {
        // First render with initial data
        await act(async () => {
            render(<TranscriptionList />);
        });

        // Enter search term
        const searchInput = screen.getByPlaceholderText('Search by audio file name');
        fireEvent.change(searchInput, { target: { value: 'test1' } });
        
        // Clear fetch mock to track new calls
        global.fetch.mockClear();
        
        // Mock the response for fetchTranscriptions after clear
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockTranscriptions
        });

        // Dispatch the custom event
        await act(async () => {
            window.dispatchEvent(new CustomEvent('clearSearchContent'));
        });

        // Check that the input was cleared
        expect(searchInput.value).toBe('');
        
        // Check that fetchTranscriptions was called
        expect(global.fetch).toHaveBeenCalledWith('http://localhost:9090/api/transcriptions');
    });

    test('handles error when fetching transcriptions', async () => {
        // Mock console.error to prevent actual errors in test output
        const originalConsoleError = console.error;
        console.error = jest.fn();

        // Clear previous mocks
        global.fetch.mockReset();
        
        // Mock a failed fetch
        global.fetch.mockRejectedValueOnce(new Error('Network error'));

        await act(async () => {
            render(<TranscriptionList />);
        });

        // Check that console.error was called
        expect(console.error).toHaveBeenCalled();
        
        // Restore console.error
        console.error = originalConsoleError;
    });
});