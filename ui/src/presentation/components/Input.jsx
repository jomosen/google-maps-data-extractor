import React from 'react';

export const Input = ({
    label,
    error,
    className = '',
    ...props
}) => {
    return (
        <div className={`flex flex-col gap-1.5 ${className}`}>
            {label && (
                <label className="text-sm font-medium text-gray-300">
                    {label}
                </label>
            )}
            <input
                className="bg-dark-hover border border-dark-border rounded-lg px-4 py-2.5 text-white 
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                   placeholder:text-gray-500 transition-all"
                {...props}
            />
            {error && (
                <span className="text-xs text-red-400">{error}</span>
            )}
        </div>
    );
};
