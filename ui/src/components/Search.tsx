"use client";

import React, { useState, useEffect } from "react";
import SearchItem from "./SearchItem";
import Modal from "./Modal";

import nextConfig from '../../next.config.mjs';

interface Entity {
  name: string;
  image: {
    path: string;
    slug: string;
  };
}

const Search: React.FC = () => {
  // const [query, setQuery] = useState('');
  const [results, setResults] = useState<Entity[]>([]);
  const [error, setError] = useState(false);
  const [isModalOpen, setModalOpen] = useState(false);
  const [activeEntity, setActiveEntity] = useState<Entity | null>(null);
  const [zoom, setZoom] = useState(0);
  const zoomLevels = ["100", "160", "200"];

  const base = nextConfig.basePath ? nextConfig.basePath + '/' : '/';

  useEffect(() => {
    fetch(base + 'logos.json')
      .then((response) => response.json())
      .then((data) => {
        setResults(data);
        setError(data.error);
      })
      .catch(() => {
        setError(true);
      });

    return () => {
      setResults([]);
    };
  }, []);

  if (error) {
    return <div>Error</div>;
  }

  if (!results) {
    return <div>Loading...</div>;
  }

  const handleZoomIn = () => {
    if (zoom < zoomLevels.length) {
      setZoom(zoom + 1);
    }
  };

  const handleZoomOut = () => {
    if (zoom > 0) {
      setZoom(zoom - 1);
    }
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === "ArrowUp") {
        handleZoomIn();
      } else if (event.ctrlKey && event.key === "ArrowDown") {
        handleZoomOut();
      } else if (event.key === "Escape") {
        setModalOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [zoom]);

  const getZoomCssValue = (): string => {
    return zoomLevels[zoom - 1] || "100";
  };

  return (
    <div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(auto-fill, minmax(${getZoomCssValue()}px, 1fr))`,
          gap: "1rem",
          color: "white",
          backgroundColor: "black",
        }}
      >
        {results.map((logo) => (
          <div
            onClick={() => {
              setModalOpen(true);
              setActiveEntity(logo);
            }}
          >
            <SearchItem
              key={logo.image.slug}
              label={logo.name}
              logoUrl={base + logo.image.path}
            />
          </div>
        ))}

        <Modal
          imageUrl={activeEntity?.image.path ?? "lol"}
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          title={activeEntity?.name ?? ""}
        />
      </div>
    </div>
  );
};

export default Search;
