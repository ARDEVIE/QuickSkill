export const environment = {
  production: true,
  // Relative (no leading slash) so it resolves against <base href>, which the
  // prod build sets to the path this project is served under (e.g.
  // /quickskill/) — see Dockerfile.prod. An absolute "/api" would instead hit
  // the shared server's root, not this project's path.
  apiUrl: 'api'
};
