import React, { useState } from 'react';

const FileUpload = () => {
    const [files, setFiles] = useState([]);

    const handleFiles = (e) => {
        setFiles([...e.target.files]);
    };

    const uploadFiles = async () => {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch('http://localhost:9090/api/transcribe', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        console.log(data);
    };

    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-md w-full max-w-md">
            <h2 className="text-3xl font-bold mb-2 text-left">File Upload</h2>
            <input
                type="file"
                multiple
                onChange={handleFiles}
                className="border border-gray-600 rounded p-2 w-full mb-2"
            />
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