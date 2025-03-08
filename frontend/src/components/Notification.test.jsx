import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import Notification from './Notification';
import '@testing-library/jest-dom';

describe('Notification', () => {
    const message = { title: 'Test Title', text: 'Test message' };

    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.runOnlyPendingTimers();
        jest.useRealTimers();
    });

    test('renders the notification with the provided message', () => {
        render(<Notification message={message} type="success" onClose={jest.fn()} />);
        expect(screen.getByText(message.title)).toBeInTheDocument();
        expect(screen.getByText(message.text)).toBeInTheDocument();
    });

    test('calls onClose after 5 seconds', () => {
        const onClose = jest.fn();
        act(() => {
            render(<Notification message={message} type="success" onClose={onClose} />);
        });

        // Initially, onClose should not have been called.
        expect(onClose).not.toHaveBeenCalled();

        // Fast-forward time by 5000ms.
        act(() => {
            jest.advanceTimersByTime(5000);
        });

        // Flush any pending setTimeout callbacks.
        act(() => {
            jest.runOnlyPendingTimers();
        });

        expect(onClose).toHaveBeenCalledTimes(1);
    });

    test('pauses and resets timer on mouse enter and resumes on mouse leave', () => {
        const onClose = jest.fn();
        
        act(() => {
            render(<Notification message={message} type="success" onClose={onClose} />);
        });
        
        const notification = screen.getByText(message.title).closest('div');

        // Advance slightly to let initial timers start
        act(() => {
            jest.advanceTimersByTime(100);
        });

        // Pause timer with mouse enter
        act(() => {
            fireEvent.mouseEnter(notification);
        });
        
        // Advance a considerable time to ensure timer is actually paused
        act(() => {
            jest.advanceTimersByTime(3000);
        });
        
        expect(onClose).not.toHaveBeenCalled();

        // Resume timer with mouse leave
        act(() => {
            fireEvent.mouseLeave(notification);
        });
        
        // Advance time to trigger the completion (full 5000ms)
        act(() => {
            jest.advanceTimersByTime(5000);
        });
        
        // Ensure any remaining timers are processed
        act(() => {
            jest.runOnlyPendingTimers();
        });
        
        expect(onClose).toHaveBeenCalledTimes(1);
    });



    test('calls onClose when the close button is clicked', () => {
        const onClose = jest.fn();
        render(<Notification message={message} type="success" onClose={onClose} />);

        const closeButton = screen.getByText('×');
        fireEvent.click(closeButton);
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
