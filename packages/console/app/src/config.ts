/**
 * Application-wide constants and configuration
 */
export const config = {
  // Base URL
  baseUrl: "https://openpatent.ai",

  // GitHub
  github: {
    repoUrl: "https://github.com/sst/openpatent",
    starsFormatted: {
      compact: "41K",
      full: "41,000",
    },
  },

  // Social links
  social: {
    twitter: "https://x.com/openpatent",
    discord: "https://discord.gg/openpatent",
  },

  // Static stats (used on landing page)
  stats: {
    contributors: "450",
    commits: "6,000",
    monthlyUsers: "400,000",
  },
} as const
