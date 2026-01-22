export * from "./client.js"
export * from "./server.js"

import { createopenpatentClient } from "./client.js"
import { createopenpatentServer } from "./server.js"
import type { ServerOptions } from "./server.js"

export async function createopenpatent(options?: ServerOptions) {
  const server = await createopenpatentServer({
    ...options,
  })

  const client = createopenpatentClient({
    baseUrl: server.url,
  })

  return {
    client,
    server,
  }
}
