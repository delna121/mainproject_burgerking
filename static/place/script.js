// see full docs and parameters:
// https://github.com/OpenCageData/geosearch
const options = {
  key: "oc_gs_codependemo74gzf48ew7fdvs91nba",
  language: "en" // de,en,es,fr
};

opencage.algoliaAutocomplete({
  container: "#place",
  placeholder: "Place",
  plugins: [opencage.OpenCageGeoSearchPlugin(options)]
});
