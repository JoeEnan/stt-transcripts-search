import React, { useEffect, useState } from 'react';

const TranscriptionList = () => {
    const [transcriptions, setTranscriptions] = useState([]);

    useEffect(() => {
        const fetchTranscriptions = async () => {
            const response = await fetch('http://localhost:9090/api/transcriptions');
            const data = await response.json();
            setTranscriptions(data);
        };
        fetchTranscriptions();
    }, []);

    return (
        <div>
            <h2>Transcriptions</h2>
            <ul>
                {transcriptions.map(transcription => (
                    <li key={transcription.id}>
                        <strong>{transcription.original_audio_filename}</strong>: {transcription.text}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default TranscriptionList;