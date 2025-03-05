import React from 'react';

const Notification = ({ message, type, onClose }) => {
    const notificationStyles = {
        success: "bg-green-500",
        successLight: "bg-green-300", // Lighter green for individual file completion
        warning: "bg-orange-500",
        error: "bg-red-500",
    };

    return (
        <div className={`fixed top-4 right-4 p-4 rounded-md shadow-lg text-white ${notificationStyles[type]}`}>
            <button onClick={onClose} className="absolute top-1 right-1 text-xl">&times;</button>
            <h4 className="font-bold">{message.title}</h4>
            <p className="pt-4">{message.text}</p>
        </div>
    );
};

export default Notification;