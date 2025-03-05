import React, { useEffect, useState } from 'react';

const TranscriptionList = () => {
    const [transcriptions, setTranscriptions] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchTranscriptions = async () => {
            const response = await fetch('http://localhost:9090/api/transcriptions');
            const data = await response.json();
            setTranscriptions(data);
        };
        fetchTranscriptions();
    }, []);

    const filteredTranscriptions = transcriptions.filter(transcription =>
        transcription.original_audio_filename.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div>
            <input
                type="text"
                placeholder="Search by audio file name"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <h2>Transcriptions</h2>
            <ul>
                {filteredTranscriptions.map(transcription => (
                    <li key={transcription.id}>
                        <strong>{transcription.original_audio_filename}</strong>: {transcription.text}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default TranscriptionList;