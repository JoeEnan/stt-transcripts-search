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
        <div className="mt-8 w-full max-w-3xl p-4 bg-gray-800 rounded-xl shadow-md">
            <h2 className="text-3xl font-bold mb-2 text-left">Past Transcriptions</h2>
            <input
                type="text"
                placeholder="Search by audio file name"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border border-gray-600 rounded p-2 w-full mb-4"
            />
            <h2 className="text-xl font-semibold mb-2">Transcriptions</h2>
            <table className="min-w-full bg-gray-800">
                <thead>
                    <tr className="bg-gray-700">
                        <th className="text-left p-3">ID</th>
                        <th className="text-left p-3">Original Filename</th>
                        <th className="text-left p-3">Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredTranscriptions.map(transcription => (
                        <React.Fragment key={transcription.id}>
                            <tr className="hover:bg-gray-600">
                                <td className="border-b border-gray-600 p-3">{transcription.id}</td>
                                <td className="border-b border-gray-600 p-3">{transcription.original_audio_filename}</td>
                                <td className="border-b border-gray-600 p-3">{new Date(transcription.created_at).toLocaleString()}</td>
                            </tr>
                            <tr>
                                <td colSpan="3" className="border-b border-gray-600 p-3">
                                    <p>{transcription.text}</p>
                                </td>
                            </tr>
                            <tr>
                                <td colSpan="3" className="border-b border-gray-600 p-3">
                                    <audio controls className="w-full">
                                        <source src={transcription.audio_filepath} type="audio/m4a" />
                                        <source src={transcription.audio_filepath.replace(/\.m4a$/, '.mp3')} type="audio/mp3" />
                                        <source src={transcription.audio_filepath.replace(/\.m4a$/, '.wav')} type="audio/wav" />
                                        Your browser does not support the audio element.
                                    </audio>
                                </td>
                            </tr>
                        </React.Fragment>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TranscriptionList;