import React from "react";

export interface ICompany {
    name: string;
    slug: string;
    image: {
      source: string;
      url: string;
    }
}

const fallbackImageUrl = 'https://via.placeholder.com/150';

export const Company: React.FC<{ company: ICompany }> = ({ company }) => {
    if (!company) {
        return <>No company data</>;
    }

    return (
        <div className="card">
            <img src={company.image?.source ?? fallbackImageUrl } alt={company.name} />
            <p>{company.name}</p>
        </div>
    );
};
