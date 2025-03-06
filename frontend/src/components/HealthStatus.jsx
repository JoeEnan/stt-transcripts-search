import React, { useEffect, useState } from 'react';

const HealthStatus = () => {
    const [status, setStatus] = useState('Checking...');
    const [isHealthy, setIsHealthy] = useState(null);

    const checkHealth = async () => {
        try {
            const response = await fetch('http://localhost:9090/api/health');
            const data = await response.json();
            if (response.ok && data.status === 'OK') {
                setStatus('API Health Status: Healthy');
                setIsHealthy(true);
            } else {
                setStatus('API Health Status: Unhealthy');
                setIsHealthy(false);
            }
        } catch (error) {
            console.error("Error checking health:", error);
            setStatus('API Health Status: Unhealthy');
            setIsHealthy(false);
        }
    };

    useEffect(() => {
        checkHealth();
        const interval = setInterval(checkHealth, 10000); // Check health every 10 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={`flex relative p-2 rounded text-gray-200 bg-gray-800
            border-2 
            ${isHealthy === true ? 'border-green-500' : isHealthy === false ? 'border-red-500' : 'border-gray-500'}
            md:absolute md:top-4 md:left-4`}>
            <h2 className="text-lg">{status}</h2>
        </div>
    );
};

export default HealthStatus;