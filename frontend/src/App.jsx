import React from 'react';
import FileUpload from './components/FileUpload';
import TranscriptionList from './components/TranscriptionList';
import HealthStatus from './components/HealthStatus';

function App() {
    return (
        /*
        Task 3a: Develop a single-page application using a modern JavaScript framework (e.g., React, Vue.js, Angular).
        Assumptions:
            - React is used, alongside TailwindCSS and Vite            
        */
        <div className="App flex flex-col items-center text-white p-4 w-screen relative">
            <h1 className="text-3xl font-bold mb-2 text-center">Audio Transcription App</h1>
            <HealthStatus />
            <FileUpload />
            <TranscriptionList />
        </div>
    );
}

export default App;