"use client";

import React from "react";
import Image from "next/image";

export interface SearchItemProps {
  logoUrl: string;
  label: string;
}

const SearchItem: React.FC<SearchItemProps> = ({ logoUrl, label }) => {
  return (
    <div
      key={label}
      className="hover:scale-120 transition:fade hover:transition-all cursor-pointer bg-gray-800 hover:bg-slate-900 p-2 rounded-sm text-center m-sm drop-shadow-lg divide-solid border-1 hover:z-4"
    >
      {/* <span className="search-item-label text-center">{label}</span> */}
      <Image src={logoUrl} alt={label} width={200} height={200} priority={true} />
    </div>
  );
};

export default SearchItem;
