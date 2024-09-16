'use client'

import React from 'react';
import Image from 'next/image';

export interface SearchItemProps {
    logoUrl: string;
    label: string;
}

const SearchItem: React.FC<SearchItemProps> = ({ logoUrl, label }) => {
    return (
        <div className='hover:scale-150 transition:fade hover:transition-all cursor-zoom-in bg-gray-800 p-5 rounded-lg text-center margin-lg drop-shadow-lg divide-solid border-1 hover:z-10'>
            <span className="search-item-label text-center">{label}</span>
            <Image src={logoUrl} alt={label} width={200} height={200} />
        </div>
    );
};

export default SearchItem;
