import React, { useState } from "react";
import Company, { ICompany } from "./Company";
import Fuse from "fuse.js";
import companyData from "../logos.json";

const Search = () => {
  const fuse = new Fuse(companyData, {
    keys: ["name", "slug"],
  });

  const [searchText, setSearchText] = useState("");
  return (
    <section>
      <input
        type="text"
        placeholder="Search..."
        onChange={(e) => setSearchText(e.target.value)}
      />

      <div className="company-grid">
        {searchText === ""
          ? companyData.map((company, index) => {
              return <Company key={index} company={company} />;
            })
          : fuse
              .search(searchText ?? "")
              .map(({ item }, index) => (
                <Company key={index} company={item as ICompany} />
              ))}
      </div>
    </section>
  );
};

export default Search;
