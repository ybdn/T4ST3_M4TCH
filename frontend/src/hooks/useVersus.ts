// Stub unique Versus (refactor en cours)
export const useVersusMatches = () => ({
  matches: [] as unknown[],
  loading: false,
  error: null as string | null,
  createMatch: async () => false,
  refreshMatches: async () => {},
  getActiveMatches: () => [] as unknown[],
  getCompletedMatches: () => [] as unknown[],
});

export const useVersusSession = () => ({
  session: null as unknown,
  loading: false,
  error: null as string | null,
  submitChoice: async () => false,
  refreshSession: async () => {},
  isWaitingForChoice: false,
  isCompleted: true,
});

export const useVersusResults = () => ({
  results: null as unknown,
  loading: false,
  error: null as string | null,
  refresh: async () => {},
  getWinner: () => null as null,
});

export const useVersusUtils = () => ({
  formatMatchStatus: () => "Indisponible",
  getMatchProgress: () => 0,
  isMyTurn: () => false,
  getWinner: () => null as null,
});
