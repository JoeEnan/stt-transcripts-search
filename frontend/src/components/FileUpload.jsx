import React, { useState } from 'react';
import Notification from './Notification';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    const [notifications, setNotifications] = useState([]);

    const handleFiles = (e) => {
        setFiles([...e.target.files]);
    };

    const uploadFiles = async () => {
        // Check if any files have been selected
        if (files.length === 0) {
            displayNotification('Error', 'Please select files for upload!', 'error', "");
            return;
        }
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch('http://localhost:9090/api/transcribe', {
            method: 'POST',
            body: formData,
        });

        // Handle the response
        if (response.ok) {
            const data = await response.json();
            displayNotification('Success', 'Files Uploaded!', 'success', 'All files');
            if (data.batch_uuid) {
                listenForTranscriptionUpdates(data.batch_uuid);
            }
        } else {
            displayNotification('Error', 'Failed to upload files.', 'error', files.map(file => file.name).join(', '));
        }

        // Clear the files after upload attempt
        setFiles([]);
        document.querySelector('input[type="file"]').value = null;
    };

    const listenForTranscriptionUpdates = (batch_uuid) => {
        const ws = new WebSocket(`ws://localhost:9090/ws/transcript_ready/${batch_uuid}`);
        ws.onopen = () => {
            console.log("Connected to WebSocket for transcription updates.");
        };
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            switch (message.status) {
                case "batch_completed":
                    displayNotification('Success', 'Batch processing is complete.', 'success', 'All files');
                    ws.close();
                    break;
                case "job_completed":
                    displayNotification('Success', `Processing complete for all audio files.`, 'success', 'All files');
                    ws.close();
                    break;
                case "completed":
                    displayNotification('Success', `Processing complete for ${message.file}.`, 'successLight', message.file);
                    break;
                case "error":
                    displayNotification('Warning', `Processing failed for ${message.file}.`, 'warning', message.file);
                    break;
                default:
                    break;
            }
        };
        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
        ws.onclose = () => {
            console.log("WebSocket connection closed.");
        };
    };

    const displayNotification = (title, text, type, affectedFiles) => {
        setNotifications(prev => [
            ...prev,
            { title, text: `File: ${affectedFiles} - ${text}`, type }
        ]);
        setTimeout(() => {
            setNotifications(prev => prev.slice(1)); // Remove oldest notification after a delay
        }, 5000);
    };

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-md w-full max-w-md">
            {notifications.map((notification, index) => (
                <Notification
                    key={index}
                    message={notification}
                    type={notification.type}
                    onClose={() => setNotifications(notifications.filter((_, i) => i !== index))}
                />
            ))}
            <h2 className="text-3xl font-bold mb-2 text-left">File Upload</h2>
            <input
                type="file"
                multiple
                onChange={handleFiles}
                className="hidden" // Hide the original input
            />
            <label className="border border-gray-600 rounded p-2 w-full mb-2 flex justify-between items-center cursor-pointer"
                onClick={() => document.querySelector('input[type="file"]').click()}>
                <span>{files.length ? `${files.length} file(s) selected` : 'Choose files'}</span>
                <span className="text-gray-500">{files.length ? '✓' : ''}</span>
            </label>
            <ul className="list-disc pl-5 mb-2 text-white">
                {Array.from(files).map((file, index) => (
                    <li key={index}>{file.name}</li>
                ))}
            </ul>
            <button
                onClick={uploadFiles}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
            >
                Upload
            </button>
        </div>
    );
};

export default FileUpload;