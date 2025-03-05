import React from 'react';
import FileUpload from './components/FileUpload';
import TranscriptionList from './components/TranscriptionList';

function App() {
    return (
        <div className="App flex flex-col items-center bg-gray-900 text-white p-4 w-screen">
            <h1 className="text-3xl font-bold mb-4 text-center">Audio Transcription App</h1>
            <FileUpload />
            <TranscriptionList />
        </div>
    );
}

export default App;