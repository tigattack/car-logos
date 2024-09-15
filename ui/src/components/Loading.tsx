import React from 'react';

const Loading: React.FC = () => {
    const spinnerStyle: React.CSSProperties = {
        width: '40px',
        height: '40px',
        border: '4px solid rgba(0, 0, 0, 0.1)',
        borderTop: '4px solid #000',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
    };

    return (
        <div style={spinnerStyle}></div>
    );
};

export default Loading;
