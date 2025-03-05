import React, { useEffect, useRef, useState } from 'react';

const Notification = ({ message, type, onClose }) => {
    const notificationStyles = {
        success: "bg-green-500",
        successLight: "bg-green-300",
        warning: "bg-orange-500",
        error: "bg-red-500",
    };

    const [duration] = useState(5000); // Duration of notification in milliseconds
    const [remainingTime, setRemainingTime] = useState(duration);
    const progressRef = useRef(null);

    useEffect(() => {
        const interval = setInterval(() => {
            setRemainingTime((time) => Math.max(time - 100, 0));
        }, 100);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (remainingTime <= 0) {
            onClose();
        }
    }, [remainingTime, onClose]);

    const handleMouseEnter = () => {
        setRemainingTime(duration); // Reset on hover
    };

    const progressPercentage = (remainingTime / duration) * 100;

    return (
        <div 
            className={`rounded-md shadow-lg text-white ${notificationStyles[type]} mb-2`}
            onMouseEnter={handleMouseEnter}
        >
            <button onClick={onClose} className="absolute top-1 right-1 text-l">&times;</button>
            <h4 className="font-bold p-4">{message.title}</h4>
            <p className="pb-4 pr-4 pl-4">{message.text}</p>
            <div className="relative">
                <div className="absolute bottom-0 left-0 h-2 bg-white" style={{ width: `${progressPercentage}%`, transition: 'width 0.1s linear' }}></div>
            </div>
        </div>
    );
};

export default Notification;