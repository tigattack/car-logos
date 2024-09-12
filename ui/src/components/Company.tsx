import React, { useEffect, useState } from "react";

export interface ICompany {
  name: string;
  slug: string;
  image: {
    source: string;
    path: string;
  };
}

const fallbackImageUrl = "https://via.placeholder.com/150";
const copiedTimeout = 1000;

export const Company: React.FC<{ company: ICompany }> = ({ company }) => {
  const [hasCopied, setHasCopied] = useState(false);

  useEffect(() => {
    if (hasCopied) {
      const timeout = setTimeout(() => {
        setHasCopied(false);
      }, copiedTimeout);
      return () => clearTimeout(timeout);
    }
  }, [hasCopied]);

  if (!company) {
    return <>No company data</>;
  }

  return (
    <div
      className="company-grid-item"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => {
        navigator.clipboard.writeText(
          window.location.href + company.image.path,
        );
        setHasCopied(true);
      }}
    >
      <img src={company.image?.source ?? fallbackImageUrl} alt={company.name} />
      <p>{company.name}</p>
      {hasCopied && <span>Copied!</span>}
    </div>
  );
};
