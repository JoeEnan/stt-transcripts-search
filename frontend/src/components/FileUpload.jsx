import React, { useState, useRef } from 'react';
import Notification from './Notification';
import { v4 as uuidv4 } from 'uuid';
import { motion } from 'framer-motion';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        setFiles([...e.target.files]);
    };

    const removeFile = (fileName) => {
        setFiles((prevFiles) => prevFiles.filter(file => file.name !== fileName));
    };

    const uploadFiles = async () => {
        if (files.length === 0) {
            displayNotification('Error', 'Please select files for upload!', 'error', "");
            return;
        }

        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        try {
            const response = await fetch('http://localhost:9090/api/transcribe', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                displayNotification('Success', 'Files Uploaded!', 'success', 'All files');

                if (data.batch_uuid) {
                    listenForTranscriptionUpdates(data.batch_uuid);
                }
            } else {
                displayNotification('Error', 'Failed to upload files.', 'error', files.map(file => file.name).join(', '));
            }
        } catch (error) {
            console.error("Upload error:", error);
            displayNotification('Error', 'An error occurred during file upload.', 'error', '');
        } finally {
            resetFileInput();
        }
    };

    const resetFileInput = () => {
        setFiles([]);
        fileInputRef.current.value = null;
    };

    const listenForTranscriptionUpdates = (batch_uuid) => {
        const ws = new WebSocket(`ws://localhost:9090/ws/transcript_ready/${batch_uuid}`);
        ws.onopen = () => console.log("Connected to WebSocket for transcription updates.");
        ws.onmessage = (event) => handleWebSocketMessage(event.data);
        ws.onerror = (error) => console.error("WebSocket error:", error);
        ws.onclose = () => console.log("WebSocket connection closed.");
    };

    const handleWebSocketMessage = (data) => {
        const message = JSON.parse(data);
        switch (message.status) {
            case "batch_completed":
                displayNotification('Success', 'Batch processing is complete.', 'success', 'All files');
                resetFileInput();
                window.dispatchEvent(new CustomEvent('clearSearchContent'));
                window.dispatchEvent(new CustomEvent('refreshTranscriptions'));
                break;
            case "job_completed":
                displayNotification('Success', 'Processing complete for all audio files.', 'success', 'All files');
                resetFileInput();
                window.dispatchEvent(new CustomEvent('clearSearchContent'));
                window.dispatchEvent(new CustomEvent('refreshTranscriptions'));
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

    const displayNotification = (title, text, type, affectedFiles) => {
        const id = uuidv4();
        setNotifications((prev) => [
            { id, title, text: `File: ${affectedFiles} - ${text}`, type },
            ...prev,
        ]);
    };

    return (
        <div className="bg-gray-800 p-4 mt-4 rounded-xl shadow-md w-full max-w-md relative">
            {/* Notifications Container */}
            <motion.div
                className="fixed top-4 right-4 flex flex-col space-y-2 z-50"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
            >
                {notifications.map((notification) => (
                    <Notification
                        key={notification.id}
                        message={notification}
                        type={notification.type}
                        onClose={() => {
                            setNotifications(prev => prev.filter((n) => n.id !== notification.id));
                        }}
                    />
                ))}
            </motion.div>
            <h2 className="text-3xl font-bold mb-2 text-left">File Upload</h2>
            <input
                id="file-input"
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                ref={fileInputRef}
            />
            <label
                htmlFor="file-input"
                className="border border-gray-600 rounded p-2 w-full mb-2 flex justify-between items-center cursor-pointer bg-gray-700 hover:bg-gray-600 transition-colors"
            >
                <span className="text-white">
                    {files.length ? `${files.length} file(s) selected` : 'Choose files'}
                </span>
                <span className="text-gray-500">{files.length ? '✓' : ''}</span>
            </label>
            <ul className="list-disc pl-5 mb-2 text-white">
                {Array.from(files).map((file, index) => (
                    <li key={index} className="flex justify-between items-center mb-2">
                        <span className="cursor-pointer">{file.name}</span>
                        <button
                            onClick={() => removeFile(file.name)}
                            className="bg-red-600 text-white rounded-full px-2 ml-2 hover:bg-red-700"
                        >
                            X
                        </button>
                    </li>
                ))}
            </ul>
            <div className="flex justify-end">
                <button
                    onClick={uploadFiles}
                    className="bg-blue-700 hover:bg-blue-800 text-white font-bold py-2 px-4 rounded transition-colors"
                >
                    Upload
                </button>
            </div>
        </div>
    );
};

export default FileUpload;