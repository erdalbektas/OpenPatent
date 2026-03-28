import { Hono } from "hono"
import { describeRoute, resolver } from "hono-openapi"
import { lazy } from "../../util/lazy"
import { OpenPatentAuth, OpenPatentUsage } from "../../auth/openpatent"
import { Installation } from "@/installation"
import { z } from "zod"

const API_BASE = "https://openpatent.techtank.com.tr"

export const OpenPatentRoutes = lazy(() => {
  const app = new Hono()

  app.post(
    "/validate",
    describeRoute({
      summary: "Validate token",
      description: "Validate an OpenPatent JWT token",
      operationId: "openpatent.validate",
      responses: {
        200: {
          description: "Validation result",
          content: {
            "application/json": {
              schema: resolver(
                z.object({
                  valid: z.boolean(),
                  userId: z.string().optional(),
                  email: z.string().optional(),
                  plan: z.string().optional(),
                }),
              ),
            },
          },
        },
      },
    }),
    async (c) => {
      const auth = await OpenPatentAuth.get()
      if (!auth?.accessToken) {
        return c.json({ valid: false })
      }

      try {
        const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${auth.accessToken}`,
          },
        })

        if (!response.ok) {
          return c.json({ valid: false })
        }

        const data = (await response.json()) as any
        return c.json({
          valid: true,
          userId: data.id,
          email: data.email,
          plan: data.plan || "free",
        })
      } catch {
        return c.json({ valid: false })
      }
    },
  )

  app.get(
    "/status",
    describeRoute({
      summary: "Get authentication status",
      description: "Get the current OpenPatent authentication status",
      operationId: "openpatent.status",
      responses: {
        200: {
          description: "Authentication status",
          content: {
            "application/json": {
              schema: resolver(
                z.object({
                  authenticated: z.boolean(),
                  userId: z.string().optional(),
                  email: z.string().optional(),
                  plan: z.string().optional(),
                  dailyActiveUsers: z.number().optional(),
                }),
              ),
            },
          },
        },
      },
    }),
    async (c) => {
      const auth = await OpenPatentAuth.get()
      const isValid = await OpenPatentAuth.isValid()
      const dailyUsers = await OpenPatentUsage.getDailyActiveUsers()

      if (!auth || !isValid) {
        return c.json({ authenticated: false })
      }

      return c.json({
        authenticated: true,
        userId: auth.userId,
        email: auth.email,
        plan: auth.plan,
        dailyActiveUsers: dailyUsers,
      })
    },
  )

  app.post(
    "/usage",
    describeRoute({
      summary: "Record usage",
      description: "Record usage for tracking daily active users",
      operationId: "openpatent.usage",
      responses: {
        200: {
          description: "Usage recorded",
          content: {
            "application/json": {
              schema: resolver(z.object({ success: z.boolean() })),
            },
          },
        },
      },
    }),
    async (c) => {
      await OpenPatentUsage.record()
      return c.json({ success: true })
    },
  )

  return app
})
