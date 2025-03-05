import React, { useEffect, useRef, useState } from 'react';

const Notification = ({ message, type, onClose }) => {
    const notificationStyles = {
        success: "bg-green-500",
        successLight: "bg-green-300",
        warning: "bg-orange-500",
        error: "bg-red-500",
    };

    const duration = 5000; // Duration of notification in milliseconds
    const [remainingTime, setRemainingTime] = useState(duration);
    const [paused, setPaused] = useState(false);
    const intervalRef = useRef(null);

    useEffect(() => {
        if (!paused) {
            intervalRef.current = setInterval(() => {
                setRemainingTime((time) => {
                    if (time <= 100) {
                        clearInterval(intervalRef.current);
                        onClose();
                        return 0;
                    }
                    return time - 100;
                });
            }, 100);
        }
        return () => {
            clearInterval(intervalRef.current);
        };
    }, [paused, onClose]);

    const handleMouseEnter = () => {
        setPaused(true);
    };

    const handleMouseLeave = () => {
        setPaused(false);
    };

    const progressPercentage = (remainingTime / duration) * 100;

    return (
        <div 
            className={`rounded-md shadow-lg text-white ${notificationStyles[type]} mb-2 relative overflow-hidden`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <button onClick={onClose} className="absolute top-1 right-1 text-l">&times;</button>
            <h4 className="font-bold p-4">{message.title}</h4>
            <p className="pb-4 pr-4 pl-4">{message.text}</p>
            <div className="relative h-2">
                <div className="absolute bottom-0 left-0 h-2 bg-white" style={{ width: `${progressPercentage}%`, transition: 'width 0.1s linear' }}></div>
            </div>
        </div>
    );
};

export default Notification;