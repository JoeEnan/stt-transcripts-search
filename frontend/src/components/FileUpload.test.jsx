/*
Task 4a: Testing for Frontend FileUpload Component
Test Setup: Mocks global fetch and WebSocket, as well as UUID generation and the Notification component.
Tests:
- renders the component with upload button: Verifies the FileUpload component displays upload-related texts.

- allows selecting files: Confirms that selected files update the display and count in the UI.

- allows removing selected files: Tests file removal functionality and checks the updated UI.

- displays error notification when trying to upload with no files: Ensures an error notification appears if no files are uploaded.

- uploads files successfully: Mocks a successful file upload and checks for notification and fetch calls.

- handles upload errors: Simulates a failed upload response and verifies the correct error notification.

- handles WebSocket messages: Tests the handling of WebSocket messages and related notifications.

- closes notification when clicked: Confirms notifications close correctly when clicked.
*/
import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from './FileUpload';

// Mock fetch globally
global.fetch = jest.fn();

// Mock WebSocket
class MockWebSocket {
    constructor(url) {
        this.url = url;
        this.onopen = null;
        this.onmessage = null;
        this.onerror = null;
        this.onclose = null;
        this.send = jest.fn();
        this.close = jest.fn();

        // Call onopen immediately for testing
        setTimeout(() => {
            if (this.onopen) this.onopen();
        }, 0);
    }
}

global.WebSocket = jest.fn().mockImplementation((url) => new MockWebSocket(url));

// Mock UUID generation to get predictable IDs
jest.mock('uuid', () => ({
    v4: () => 'test-uuid'
}));

// Mock the Notification component
jest.mock('./Notification', () => {
    return function MockNotification({ message, onClose }) {
        return (
            <div data-testid="notification" onClick={onClose}>
                <div data-testid="notification-title">{message.title}</div>
                <div data-testid="notification-text">{message.text}</div>
                <div data-testid="notification-type">{message.type}</div>
            </div>
        );
    };
});

// Mock framer-motion
jest.mock('framer-motion', () => ({
    motion: {
        div: ({ children, ...props }) => (
            <div data-testid="motion-div" {...props}>
                {children}
            </div>
        ),
    },
}));

describe('FileUpload', () => {
    beforeEach(() => {
        // Reset all mocks before each test
        jest.clearAllMocks();

        // Mock CustomEvent
        global.CustomEvent = jest.fn((event, options) => ({
            type: event,
            ...options
        }));

        // Mock dispatchEvent
        window.dispatchEvent = jest.fn();
    });

    test('renders the component with upload button', () => {
        render(<FileUpload />);
        expect(screen.getByText('File Upload')).toBeInTheDocument();
        expect(screen.getByText('Choose files')).toBeInTheDocument();
        expect(screen.getByText('Upload')).toBeInTheDocument();
    });

    test('allows selecting files', async () => {
        render(<FileUpload />);

        const fileInput = screen.getByLabelText('Choose files');

        // Create mock files
        const file1 = new File(['file1 content'], 'file1.m4a', { type: 'audio/m4a' });
        const file2 = new File(['file2 content'], 'file2.m4a', { type: 'audio/m4a' });

        // Simulate file selection
        await act(async () => {
            fireEvent.change(fileInput, {
                target: {
                    files: [file1, file2]
                }
            });
        });

        // Check that the file count is displayed
        expect(screen.getByText('2 file(s) selected')).toBeInTheDocument();

        // Check that file names are displayed
        expect(screen.getByText('file1.m4a')).toBeInTheDocument();
        expect(screen.getByText('file2.m4a')).toBeInTheDocument();
    });

    test('allows removing selected files', async () => {
        render(<FileUpload />);

        const fileInput = screen.getByLabelText('Choose files');

        // Create mock files
        const file1 = new File(['file1 content'], 'file1.m4a', { type: 'audio/m4a' });
        const file2 = new File(['file2 content'], 'file2.m4a', { type: 'audio/m4a' });

        // Simulate file selection
        await act(async () => {
            fireEvent.change(fileInput, {
                target: {
                    files: [file1, file2]
                }
            });
        });

        // Get remove buttons (X)
        const removeButtons = screen.getAllByText('X');

        // Remove the first file
        await act(async () => {
            fireEvent.click(removeButtons[0]);
        });

        // Check that only the second file remains
        expect(screen.queryByText('file1.m4a')).not.toBeInTheDocument();
        expect(screen.getByText('file2.m4a')).toBeInTheDocument();
        expect(screen.getByText('1 file(s) selected')).toBeInTheDocument();
    });

    test('displays error notification when trying to upload with no files', async () => {
        render(<FileUpload />);

        // Click upload with no files selected
        const uploadButton = screen.getByText('Upload');
        await act(async () => {
            fireEvent.click(uploadButton);
        });

        // Check for error notification
        expect(screen.getByTestId('notification-title')).toHaveTextContent('Error');
        expect(screen.getByTestId('notification-text')).toHaveTextContent('Please select files for upload!');
        expect(screen.getByTestId('notification-type')).toHaveTextContent('error');
    });

    test('uploads files successfully', async () => {
        render(<FileUpload />);

        const fileInput = screen.getByLabelText('Choose files');

        // Create mock file
        const file = new File(['file content'], 'test.m4a', { type: 'audio/m4a' });

        // Simulate file selection
        await act(async () => {
            fireEvent.change(fileInput, {
                target: {
                    files: [file]
                }
            });
        });

        // Mock successful upload response
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ batch_uuid: 'test-batch-uuid' })
        });

        // Click upload
        const uploadButton = screen.getByText('Upload');
        await act(async () => {
            fireEvent.click(uploadButton);
        });

        // Check that fetch was called with the right arguments
        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:9090/api/transcribe',
            expect.objectContaining({
                method: 'POST',
                body: expect.any(FormData)
            })
        );

        // Check for success notification
        expect(screen.getByTestId('notification-title')).toHaveTextContent('Success');
        expect(screen.getByTestId('notification-text')).toHaveTextContent('File: All files - Files Uploaded!');

        // Check that WebSocket was initialized
        expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:9090/ws/transcript_ready/test-batch-uuid');
    });

    test('handles upload errors', async () => {
        render(<FileUpload />);

        const fileInput = screen.getByLabelText('Choose files');

        // Create mock file
        const file = new File(['file content'], 'test.m4a', { type: 'audio/m4a' });

        // Simulate file selection
        await act(async () => {
            fireEvent.change(fileInput, {
                target: {
                    files: [file]
                }
            });
        });

        // Mock failed upload response
        global.fetch.mockResolvedValueOnce({
            ok: false
        });

        // Click upload
        const uploadButton = screen.getByText('Upload');
        await act(async () => {
            fireEvent.click(uploadButton);
        });

        // Check for error notification
        expect(screen.getByTestId('notification-title')).toHaveTextContent('Error');
        expect(screen.getByTestId('notification-text')).toHaveTextContent('Failed to upload files');
    });

    test('handles WebSocket messages', async () => {
        // Render the component
        render(<FileUpload />);

        // Select and upload a file to initialize WebSocket
        const fileInput = screen.getByLabelText('Choose files');
        const file = new File(['content'], 'test.m4a', { type: 'audio/m4a' });

        await act(async () => {
            fireEvent.change(fileInput, { target: { files: [file] } });
        });

        // Mock successful upload response
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ batch_uuid: 'test-batch-uuid' })
        });

        await act(async () => {
            fireEvent.click(screen.getByText('Upload'));
        });

        // Get the WebSocket instance that was created
        const wsInstance = global.WebSocket.mock.results[0].value;

        // Simulate WebSocket messages by directly calling the callback
        await act(async () => {
            // Simulate a message event for batch_completed
            wsInstance.onmessage?.({
                data: JSON.stringify({ status: 'batch_completed' })
            });
        });

        // Check that events were dispatched
        expect(window.dispatchEvent).toHaveBeenCalledWith(expect.objectContaining({
            type: 'clearSearchContent'
        }));
        expect(window.dispatchEvent).toHaveBeenCalledWith(expect.objectContaining({
            type: 'refreshTranscriptions'
        }));

        // Check for notification
        await waitFor(() => {
            const notificationTitles = screen.getAllByTestId('notification-title');
            const batchCompleteTitle = Array.from(notificationTitles).find(
                title => title.textContent === 'Success'
            );
            expect(batchCompleteTitle).toBeTruthy();
        });

        // Test job_completed message
        await act(async () => {
            wsInstance.onmessage?.({
                data: JSON.stringify({ status: 'job_completed' })
            });
        });

        // Test completed message
        await act(async () => {
            wsInstance.onmessage?.({
                data: JSON.stringify({ status: 'completed', file: 'test.m4a' })
            });
        });

        // Test error message
        await act(async () => {
            wsInstance.onmessage?.({
                data: JSON.stringify({ status: 'error', file: 'test.m4a' })
            });
        });

        // Check for notifications
        expect(screen.getAllByTestId('notification-title').length).toBeGreaterThanOrEqual(4);
    });

    test('closes notification when clicked', async () => {
        render(<FileUpload />);

        // Create a notification
        const uploadButton = screen.getByText('Upload');
        await act(async () => {
            fireEvent.click(uploadButton);
        });

        // Should have an error notification
        const notification = screen.getByTestId('notification');

        // Click the notification to close it
        await act(async () => {
            fireEvent.click(notification);
        });

        // Check that notification is removed
        expect(screen.queryByTestId('notification')).not.toBeInTheDocument();
    });
});