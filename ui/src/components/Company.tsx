import React, { useEffect, useState } from "react";
import { LazyLoadImage, trackWindowScroll } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import Loading from "./Loading";

export interface ICompany {
  name: string;
  slug: string;
  image: {
    source: string;
    path: string;
  };
}

const copiedTimeout = 1000;

const Company: React.FC<{ company: ICompany}> = ({ company, scrollPosition }) => {
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
      onClick={() => {
        navigator.clipboard.writeText(
          window.location.href + company.image.path,
        );
        setHasCopied(true);
      }}
    >
      <LazyLoadImage
        key={company.slug}
        src={company.image.path}
        alt={company.slug}
        effect={"blur"}
        width={"185px"}
        height={"140px"}
        scrollPosition={scrollPosition}
        visibleByDefault={false}
        placeholder={<Loading />}
      />
      <p>{company.name}</p>
      {hasCopied && <span>Copied!</span>}
    </div>
  );
};


export default trackWindowScroll(Company)
