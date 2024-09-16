'use client'

import React, { useState, useEffect } from 'react';

import SearchItem from './SearchItem';

import nextConfig from '../../next.config.mjs';

interface Entity {
  label: string
  image: {
    path: string,
    slug: string
  }
}

const Search: React.FC = () => {
  // const [query, setQuery] = useState('');
  const [results, setResults] = useState<Entity[]>([]);
  const [error, setError] = useState(false);

  const base = nextConfig.basePath ? nextConfig.basePath + '/' : '/';

  useEffect(() => {
    fetch(base + 'logos.json')
      .then((response) => response.json())
      .then((data) => {
        setResults(data);
        setError(data.error);

        // TODO: Fix this.
        // It's annoying we dont have a server
        // if (!query) return
        // const filteredLogos = results.filter((entity: Entity) => {
        //     console.log(entity);
        // });
      }).catch(() => {
        setError(true);
      });

    return () => {
      setResults(results ?? []);
    }
  }, []);

  if (error) {
    return <div>Error</div>;
  }

  if (!results) {
    return <div>Loading...</div>;
  }

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
          <SearchItem key={logo.image.slug} logoUrl={base + logo.image.path} label={logo.label} />
        ))}
      </div>
    </div>
  );
};

export default Search;
