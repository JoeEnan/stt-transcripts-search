import React, { useState } from 'react';

const FileUpload = () => {
    const [files, setFiles] = useState([]);
    
    const handleFiles = (e) => {
        setFiles([...e.target.files]);
    };

    const uploadFiles = async () => {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file); // make sure to match with backend code
        });

        const response = await fetch('http://localhost:9090/api/transcribe', {
            method: 'POST',
            body: formData, 
        });

        const data = await response.json();
        console.log(data);
    };

    return (
        <div>
            <input type="file" multiple onChange={handleFiles} />
            <button onClick={uploadFiles}>Upload</button>
        </div>
    );
};

export default FileUpload;