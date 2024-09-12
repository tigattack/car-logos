export const imgdbMock = [
  {
    name: "Land Rover",
    slug: "land-rover",
    image: {
      source: "https://www.carlogos.org/car-logos/land-rover-logo.png",
      url: "/land-rover.png",
    },
  },
  {
    name: "Volkswagen",
    slug: "volkswagen",
    image: {
      source: "https://www.carlogos.org/car-logos/volkswagen-logo.png",
      url: "/volkswagen.png",
    },
  },
];

export const imgDbMockFactory = (count: number) => {
  return Array.from({ length: count }, (_, index) => ({
    name: `Company ${index + 1}`,
    slug: `company-${index + 1}`,
    image: {
      source: `https://www.carlogos.org/car-logos/company-${index + 1}-logo.png`,
      url: `/company-${index + 1}.png`,
    },
  }));
};
