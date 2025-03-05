// src/App.jsx

import React from 'react';
import FileUpload from './components/FileUpload';
import TranscriptionList from './components/TranscriptionList';

function App() {
    return (
        <div className="App flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
            <h1 className="text-3xl font-bold mb-4">Audio Transcription App</h1>
            <FileUpload />
            <TranscriptionList />
        </div>
    );
}

export default App;