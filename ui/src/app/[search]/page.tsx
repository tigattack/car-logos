'use client'
import React, { Suspense, useEffect, useState } from "react";
// import Company, { ICompany } from "./Company";
import Fuse from "fuse.js";
import SearchItem, { SearchItemProps } from "@/components/SearchItem";

const dataUrl = "/logos.json";

const Page: React.FC = () => {
  const [searchData, setSearchData] = useState<SearchItemProps[]>([]);
  const [searchText, setSearchText] = useState("");


  const fuse = new Fuse(searchData, {
    keys: ["name", "slug"], threshold: 0.3
});




  useEffect(() => {
    fetch(dataUrl)
      .then((response) => response.json())
      .then((data) => {
        setSearchData(data);
      });
  }, []);

  return (
    <section>
      <input
        type="text"
        placeholder="Search..."
        onChange={(e) => setSearchText(e.target.value)}
      />

      <div className="company-grid">
        {searchText === ""
          ? searchData.map((entity, index) => {
            <div>COMPANY</div>
              return <SearchItem key={index} logoUrl={entity.logoUrl} label={entity.label} />;
            })
          : fuse
              .search(searchText ?? "")
              .map(({ item }, index) => (
                <Suspense fallback={<div>Loading...</div>}>
                    <div>ITEM</div>
                  {/* <Company key={index} company={item as ICompany} /> */}
                </Suspense>
              ))}
      </div>
    </section>
  );
};

export default Page;


