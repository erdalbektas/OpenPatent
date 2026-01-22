const stage = process.env.SST_STAGE || "dev"

export default {
  url: stage === "production" ? "https://openpatent.ai" : `https://${stage}.openpatent.ai`,
  console: stage === "production" ? "https://openpatent.ai/auth" : `https://${stage}.openpatent.ai/auth`,
  email: "contact@anoma.ly",
  socialCard: "https://social-cards.sst.dev",
  github: "https://github.com/sst/openpatent",
  discord: "https://openpatent.ai/discord",
  headerLinks: [
    { name: "Home", url: "/" },
    { name: "Docs", url: "/docs/" },
  ],
}
