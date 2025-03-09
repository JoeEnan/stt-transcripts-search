/*
Task 4a: Testing for Frontend HealthStatus Component
Test Setup: Uses fake timers to control interval behavior for health checks; cleans up after each test.
Tests:
- displays healthy status when API returns OK: 
    - Mocks a successful API response and checks for healthy status in the UI.

- displays unhealthy status when API does not return OK or fetch fails: 
    - Validates that the UI updates correctly for both a failed API response and a fetch error.
*/
import React from 'react';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import HealthStatus from './HealthStatus';
import '@testing-library/jest-dom';

afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
    jest.useRealTimers();
});

describe('HealthStatus component', () => {
    // Use fake timers to control setInterval behavior.
    beforeEach(() => {
        jest.useFakeTimers();
    });

    test('displays healthy status when API returns OK', async () => {
        // Mock the fetch function to simulate a healthy response.
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'OK' }),
        });

        render(<HealthStatus />);

        // Initially 'Checking...' should render.
        expect(screen.getByText('Checking...')).toBeInTheDocument();

        // Fast-forward until all timers have been executed.
        jest.runOnlyPendingTimers();

        // Wait for the status update.
        await waitFor(() => {
            expect(screen.getByText('API Health Status: Healthy')).toBeInTheDocument();
        });

        // Check if the container uses the healthy border class.
        const container = screen.getByText('API Health Status: Healthy').parentElement;
        expect(container).toHaveClass('border-green-500');
    });

    test('displays unhealthy status when API does not return OK or fetch fails', async () => {
        // Simulate an unhealthy API response.
        global.fetch = jest.fn().mockResolvedValue({
            ok: false,
            json: async () => ({ status: 'Not OK' }),
        });

        render(<HealthStatus />);
        jest.runOnlyPendingTimers();

        await waitFor(() => {
            expect(screen.getByText('API Health Status: Unhealthy')).toBeInTheDocument();
        });

        const container = screen.getByText('API Health Status: Unhealthy').parentElement;
        expect(container).toHaveClass('border-red-500');

        // Now simulate a fetch error.
        global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
        // Re-render the component to simulate another check or use a custom approach.
        cleanup();
        render(<HealthStatus />);
        jest.runOnlyPendingTimers();

        await waitFor(() => {
            expect(screen.getByText('API Health Status: Unhealthy')).toBeInTheDocument();
        });
        const errorContainer = screen.getByText('API Health Status: Unhealthy').parentElement;
        expect(errorContainer).toHaveClass('border-red-500');
    });
});