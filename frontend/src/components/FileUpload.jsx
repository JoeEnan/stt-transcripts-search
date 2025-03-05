import React, { useState } from 'react';

const FileUpload = () => {
    const [files, setFiles] = useState([]);

    const handleFiles = (e) => {
        setFiles([...e.target.files]);
    };

    const uploadFiles = async () => {
        // Check if any files have been selected
        if (files.length === 0) {
            console.warn("No files selected for upload.");
            return; // Exit the function if no files are selected
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
            console.log("Files uploaded, transcription started:", data);
            if (data.batch_uuid) {
                listenForTranscriptionUpdates(data.batch_uuid);
            }
        } else {
            const errorText = await response.text();
            console.error("Failed to upload files:", errorText);
        }

        // Clear the files after upload attempt
        setFiles([]);
        document.querySelector('input[type="file"]').value = null; // Reset the file input
    };

    const listenForTranscriptionUpdates = (batch_uuid) => {
        const ws = new WebSocket(`ws://localhost:9090/ws/transcript_ready/${batch_uuid}`);
        ws.onopen = () => {
            console.log("Connected to WebSocket for transcription updates.");
        };
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log("Received from websocket:", message);
            // Check if the batch is completed
            if (message.status === "batch_completed") {
                console.log("Batch processing is complete.");
                ws.close();  // Close the WebSocket connection
            }
            // Else, its a single audio file job that is completed
            else if (message.status === "job_completed") {
                console.log("Audio file processing is complete.");
                ws.close();  // Close the WebSocket connection
            }
        };
        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
        ws.onclose = () => {
            console.log("WebSocket connection closed.");
        };
    };

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-md w-full max-w-md">
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