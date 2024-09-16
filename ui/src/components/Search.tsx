'use client'

import React, { useState, useEffect } from 'react';

import SearchItem from './SearchItem';

interface Entity {
    id: number;
    name: string;
    url: string;
}

const Search: React.FC = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Entity[]>([]);

    useEffect(() => {
        fetch('/logos.json')
        .then((response) => response.json())
        .then((data) => {
            setResults(data);

            // TODO: Fix this.
            // It's annoying we dont have a server
            // if (!query) return
            // const filteredLogos = results.filter((entity: Entity) => {
            //     console.log(entity);
            // });
        });

        return () => {
            setResults(results ?? []);
        }
    }, [query]);

    return (
        <div>
            {/* <input
                type="text"
                placeholder="Search logos..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            /> */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '.5rem' }}>
                {results.map((logo) => (
                    <SearchItem key={logo.id} logoUrl={'/' + logo.image.path} label={logo.name} />
                ))}
            </div>
        </div>
    );
};

export default Search;
