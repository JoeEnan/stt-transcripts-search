import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

const Notification = ({ message, type, onClose }) => {
    const accentColors = {
        success: "border-green-500",
        successLight: "border-green-300",
        warning: "border-yellow-500",
        error: "border-red-500",
    };
  
    const progressBarColors = {
        success: "bg-green-500",
        successLight: "bg-green-300",
        warning: "bg-yellow-500",
        error: "bg-red-500",
    };
  
    const duration = 5000; // Duration of notification in milliseconds
    const [remainingTime, setRemainingTime] = useState(duration);
    const intervalRef = useRef(null);
  
    const startTimer = () => {
        intervalRef.current = setInterval(() => {
            setRemainingTime((time) => {
                if (time <= 100) {
                    clearInterval(intervalRef.current);
                    // Use setTimeout to ensure onClose is called after the current render cycle
                    setTimeout(() => onClose(), 0);
                    return 0;
                }
                return time - 100;
            });
        }, 100);
    };

    useEffect(() => {
        startTimer();
        return () => clearInterval(intervalRef.current);
    }, [onClose]);

    const handleMouseEnter = () => {
        clearInterval(intervalRef.current);
        setRemainingTime(duration); // Reset timer
    };
  
    const handleMouseLeave = () => {
        clearInterval(intervalRef.current);
        startTimer(); // Restart timer
    };
  
    const progressPercentage = (remainingTime / duration) * 100;

    return (
        <motion.div
            className={`rounded-md shadow-lg text-gray-200 bg-gray-800 border-l-4 ${accentColors[type]} mb-2 relative overflow-hidden`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            initial={{ opacity: 0, transform: 'translateY(-20px)' }}
            animate={{ opacity: 1, transform: 'translateY(0)' }}
            exit={{ opacity: 0, transform: 'translateY(-20px)' }}
            transition={{ duration: 0.2 }}
        >
            <button 
                onClick={onClose} 
                className={`absolute top-1 right-1 text-xl text-gray-300 hover:text-white transition-colors`}
            >
                &times;
            </button>
            <h4 className="font-bold p-4">{message.title}</h4>
            <p className="pb-4 pr-4 pl-4">{message.text}</p>
            <div className="relative h-2">
                <div
                    className={`absolute bottom-0 left-0 h-2 ${progressBarColors[type]} transition-width duration-200`}
                    style={{ width: `${progressPercentage}%` }}
                />
            </div>
        </motion.div>
    );
};

export default Notification;