import { z } from "zod"

export const PatentHit = z.object({
  id: z.string(),
  title: z.string(),
  abstract: z.string().optional(),
  date: z.string().optional(),
  assignee: z.string().optional(),
})
export type PatentHit = z.infer<typeof PatentHit>

export const SearchResult = z.object({
  provider: z.string(),
  query: z.string(),
  hits: z.array(PatentHit),
})
export type SearchResult = z.infer<typeof SearchResult>

export type SearchProvider = {
  id: string
  search(query: string, options?: { limit?: number }): Promise<SearchResult>
}

export class SearchNotConfiguredError extends Error {
  constructor(message = "Patent search is not configured. Set PATENTSVIEW_API_KEY for USPTO PatentsView.") {
    super(message)
    this.name = "SearchNotConfiguredError"
  }
}

export function createPatentsViewProvider(apiKey: string | undefined): SearchProvider {
  return {
    id: "patentsview",
    async search(query, options = {}) {
      if (!apiKey?.trim()) throw new SearchNotConfiguredError()

      const limit = options.limit ?? 10
      const url = new URL("https://search.patentsview.org/api/v1/patent/")
      url.searchParams.set("q", JSON.stringify({ _text_any: { patent_title: query, patent_abstract: query } }))
      url.searchParams.set("f", JSON.stringify(["patent_id", "patent_title", "patent_abstract", "patent_date"]))
      url.searchParams.set("o", JSON.stringify({ per_page: limit }))

      const res = await fetch(url, {
        headers: {
          "X-Api-Key": apiKey,
          Accept: "application/json",
        },
      })

      if (!res.ok) {
        const body = await res.text()
        throw new Error(`PatentsView request failed (${res.status}): ${body.slice(0, 200)}`)
      }

      const data = (await res.json()) as {
        patents?: Array<{
          patent_id?: string
          patent_title?: string
          patent_abstract?: string
          patent_date?: string
        }>
      }

      const hits: PatentHit[] = (data.patents ?? []).map((p) => ({
        id: p.patent_id ?? "unknown",
        title: p.patent_title ?? "",
        abstract: p.patent_abstract,
        date: p.patent_date,
      }))

      return { provider: "patentsview", query, hits }
    },
  }
}

export function resolveSearchProvider(env: Record<string, string | undefined> = process.env): SearchProvider {
  return createPatentsViewProvider(env.PATENTSVIEW_API_KEY)
}
