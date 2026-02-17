import React from 'react';
import { motion } from 'framer-motion';

export const Card = ({ children, className = '', hover = false, ...props }) => {
    return (
        <motion.div
            whileHover={hover ? { y: -2, boxShadow: '0 8px 30px rgba(99, 102, 241, 0.1)' } : {}}
            className={`bg-dark-surface border border-dark-border rounded-xl p-6 ${className}`}
            {...props}
        >
            {children}
        </motion.div>
    );
};
