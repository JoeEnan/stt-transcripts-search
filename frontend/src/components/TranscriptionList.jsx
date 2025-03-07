import React, { useEffect, useState } from 'react';
import matchCaseIcon from '../assets/match-case.svg';
import fullFileIcon from '../assets/match_full_file_name.svg';

const TranscriptionList = () => {
    const [transcriptions, setTranscriptions] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [matchFullFileName, setMatchFullFileName] = useState(false);
    const [matchCase, setMatchCase] = useState(false);

    // Function to fetch all transcriptions
    const fetchTranscriptions = async () => {
        try {
            const response = await fetch('http://localhost:9090/api/transcriptions');
            const data = await response.json();
            setTranscriptions(data);
        } catch (error) {
            console.error("Error fetching transcriptions:", error);
        }
    };

    // Function to search transcriptions with additional query parameters
    const searchTranscriptions = async (term) => {
        if (!term) {
            fetchTranscriptions();
            return;
        }
        try {
            const params = new URLSearchParams({
                file_name: term,
                match_full_file_name: matchFullFileName,
                match_case: matchCase,
            });
            const response = await fetch(`http://localhost:9090/api/search?${params.toString()}`);
            const data = await response.json();
            setTranscriptions(data);
        } catch (error) {
            console.error("Error searching transcriptions:", error);
        }
    };

    useEffect(() => {
        // Fetch all transcriptions on component mount
        fetchTranscriptions();
        const clearSearchListener = () => {
            handleClearSearch();
        };

        window.addEventListener('clearSearchContent', clearSearchListener);
        return () => {
            window.removeEventListener('clearSearchContent', clearSearchListener);
        };
    }, []);

    // When triggering search, check for Enter or click event.
    const handleSearch = (e) => {
        if (e.type === 'click' || e.key === 'Enter') {
            searchTranscriptions(searchTerm);
        }
    };

    // Clear the search term and reset toggles
    const handleClearSearch = () => {
        setSearchTerm('');
        setMatchFullFileName(false);
        setMatchCase(false);
        fetchTranscriptions();
    };

    const toggleFullFileName = () => {
        setMatchFullFileName(prev => !prev);
    };

    const toggleMatchCase = () => {
        setMatchCase(prev => !prev);
    };

    return (
        <div className="mt-8 w-full max-w-3xl p-4 bg-gray-800 rounded-xl shadow-md">
            <h2 className="text-3xl font-bold mb-2 text-left">Past Transcriptions</h2>
            <div className="flex flex-col gap-2">
                <div className="relative">
                    <input
                        type="text"
                        placeholder="Search by audio file name"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyDown={handleSearch} // Trigger search on Enter key press
                        className="border border-gray-600 rounded p-2 w-full pr-28" // Extra right padding for icons
                    />
                    {/* Icon toggle buttons positioned inside input field */}
                    <div className="absolute inset-y-0 right-0 flex items-center pr-2 space-x-2">
                        <div className={`relative p-0.5 ${matchFullFileName ? 'border border-white rounded-sm' : ''}`}>
                            <img
                                src={fullFileIcon}
                                alt="Match Full File Name"
                                onClick={toggleFullFileName}
                                className={`cursor-pointer w-6 h-6 ${matchFullFileName ? 'opacity-100' : 'opacity-100'}`}
                                title="Toggle Match Whole Word"
                            />
                        </div>
                        <div className={`relative p-0.5 ${matchCase ? 'border border-white rounded-sm' : ''}`}>
                            <img
                                src={matchCaseIcon}
                                alt="Match Case"
                                onClick={toggleMatchCase}
                                className={`cursor-pointer w-6 h-6 ${matchCase ? 'opacity-100' : 'opacity-100'}`}
                                title="Toggle Match Case"
                            />
                        </div>
                    </div>
                </div>
                <div className="flex justify-between">
                    <button
                        onClick={handleClearSearch}
                        className="px-4 py-2 bg-red-700 text-white rounded hover:bg-red-800"
                    >
                        Clear Search
                    </button>
                    <button
                        onClick={handleSearch}
                        className="px-4 py-2 bg-blue-700 text-white rounded hover:bg-blue-800"
                    >
                        Search
                    </button>
                </div>
            </div>

            <h2 className="text-xl font-semibold mb-2 mt-6">Transcriptions</h2>
            <table className="min-w-full bg-gray-800">
                <thead>
                    <tr className="bg-gray-700">
                        <th className="text-left p-3">ID</th>
                        <th className="text-left p-3">Original Filename</th>
                        <th className="text-left p-3">Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {transcriptions.map(transcription => (
                        <React.Fragment key={transcription.id}>
                            <tr className="hover:bg-gray-600">
                                <td className="border-b border-gray-600 p-3">{transcription.id}</td>
                                <td className="border-b border-gray-600 p-3">{transcription.original_audio_filename}</td>
                                <td className="border-b border-gray-600 p-3">
                                    {new Date(transcription.created_at).toLocaleString()}
                                </td>
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