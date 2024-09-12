import React from "react";
import data from "../logos.json";
import Fuse from "fuse.js";

const fuse = new Fuse(data, {
  keys: ["name", "slug"],
});

export const View = () => {
  return fuse.search(window.location.pathname).map(({ item }, index) => {
    return (
      <div key={index}>
        <h1>{item.name}</h1>
        <img src={item.image.source} alt={item.name} />
      </div>
    );
  });
};
