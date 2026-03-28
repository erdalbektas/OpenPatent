import path from "path"
import { Global } from "../global"
import z from "zod"
import { Filesystem } from "../util/filesystem"
import { Log } from "../util/log"

const log = Log.create({ service: "auth.openpatent" })

const API_BASE = "https://openpatent.techtank.com.tr"
const VERIFY_CACHE_TTL = 5 * 60 * 1000 // 5 minutes

let verifyCache = { valid: false, expiresAt: 0 }

export const AuthSchema = z
  .object({
    type: z.literal("openpatent"),
    accessToken: z.string(),
    refreshToken: z.string().optional(),
    userId: z.string().optional(),
    email: z.string().optional(),
    plan: z.enum(["free", "pro", "enterprise"]).default("free"),
    expiresAt: z.number().optional(),
    createdAt: z.number(),
  })
  .meta({ ref: "OpenPatentAuth" })

export type AuthData = z.infer<typeof AuthSchema>

const filepath = path.join(Global.Path.data, "auth-openpatent.json")

async function refreshToken(refreshToken: string): Promise<AuthData | undefined> {
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    })

    if (!response.ok) {
      log.warn("token refresh failed", { status: response.status })
      return undefined
    }

    const data = (await response.json()) as any
    const current = await Filesystem.readJson<AuthData>(filepath).catch(() => null)
    if (!current) return undefined

    const updated: AuthData = {
      ...current,
      accessToken: data.access,
      refreshToken: data.refresh ?? current.refreshToken,
      expiresAt: data.expires * 1000,
      createdAt: current.createdAt,
    }

    await Filesystem.writeJson(filepath, updated, 0o600)
    return updated
  } catch (error) {
    log.error("token refresh error", { error })
    return undefined
  }
}

export const OpenPatentAuth = {
  async get(): Promise<AuthData | undefined> {
    const data = await Filesystem.readJson<unknown>(filepath).catch(() => null)
    if (!data) return undefined
    const parsed = AuthSchema.safeParse(data)
    if (!parsed.success) {
      log.warn("invalid auth data", { error: parsed.error })
      return undefined
    }

    const auth = parsed.data

    if (auth.expiresAt && auth.expiresAt < Date.now()) {
      if (auth.refreshToken) {
        const refreshed = await refreshToken(auth.refreshToken)
        if (refreshed) {
          return refreshed
        }
      }
      return undefined
    }

    return auth
  },

  async set(auth: Omit<AuthData, "createdAt" | "type"> & { createdAt?: number }) {
    const existing = await Filesystem.readJson<AuthData>(filepath).catch(() => null)
    const data: AuthData = {
      type: "openpatent",
      ...auth,
      createdAt: existing?.createdAt ?? Date.now(),
    }
    await Filesystem.writeJson(filepath, data, 0o600)
    log.info("auth saved", { userId: auth.userId, email: auth.email })
  },

  async remove() {
    await Filesystem.remove(filepath).catch(() => {})
    log.info("auth removed")
  },

  // Quick local check - for performance
  async isValid(): Promise<boolean> {
    const auth = await this.get()
    if (!auth) return false
    if (auth.expiresAt && auth.expiresAt < Date.now()) {
      return false
    }
    return true
  },

  // Server verification with caching - for security
  // Call this when you need to ensure token is truly valid
  // Caches result for 5 minutes to avoid excessive server calls
  async isValidServer(): Promise<boolean> {
    const auth = await this.get()
    if (!auth) return false

    // Check if we have a recent verification
    const now = Date.now()
    if (verifyCache.valid && verifyCache.expiresAt > now) {
      return verifyCache.valid
    }

    // Verify with server
    const result = await this.verify()

    // Cache result
    verifyCache = {
      valid: result.valid,
      expiresAt: now + VERIFY_CACHE_TTL,
    }

    return result.valid
  },

  async getAccessToken(): Promise<string | undefined> {
    const auth = await this.get()
    return auth?.accessToken
  },

  async login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        return { success: false, error: error.message || "Login failed" }
      }

      const data = (await response.json()) as any

      await this.set({
        accessToken: data.access,
        refreshToken: data.refresh,
        userId: data.user?.id,
        email: data.user?.email,
        plan: data.user?.plan || "free",
        expiresAt: data.expires * 1000,
      })

      log.info("login successful", { email })
      return { success: true }
    } catch (error) {
      log.error("login error", { error })
      return { success: false, error: "Connection error" }
    }
  },

  async logout(): Promise<void> {
    const auth = await this.get()
    if (auth?.accessToken) {
      try {
        await fetch(`${API_BASE}/api/v1/auth/logout`, {
          method: "POST",
          headers: { Authorization: `Bearer ${auth.accessToken}` },
        }).catch(() => {})
      } catch {}
    }
    verifyCache = { valid: false, expiresAt: 0 }
    await this.remove()
  },

  async verify(): Promise<{ valid: boolean; userId?: string; email?: string; plan?: string }> {
    const auth = await this.get()
    if (!auth?.accessToken) {
      return { valid: false }
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${auth.accessToken}`,
        },
        body: JSON.stringify({ token: auth.accessToken }),
      })

      if (!response.ok) {
        log.warn("token verification failed", { status: response.status })
        return { valid: false }
      }

      const data = (await response.json()) as any

      // Update local data with server data (plan might have changed)
      if (data.user) {
        await this.set({
          accessToken: auth.accessToken,
          refreshToken: auth.refreshToken,
          userId: data.user.id,
          email: data.user.email,
          plan: data.user.plan || auth.plan,
          expiresAt: auth.expiresAt,
        })
      }

      return {
        valid: true,
        userId: data.user?.id,
        email: data.user?.email,
        plan: data.user?.plan,
      }
    } catch (error) {
      log.error("token verification error", { error })
      // Don't invalidate on network error - be lenient
      return { valid: true, userId: auth.userId, email: auth.email, plan: auth.plan }
    }
  },
}

const usageFilepath = path.join(Global.Path.data, "usage.json")

interface UsageEntry {
  lastSeen: number
  date: string
}

export const OpenPatentUsage = {
  async record() {
    const today = new Date().toISOString().split("T")[0]
    const data = await Filesystem.readJson<Record<string, UsageEntry>>(usageFilepath).catch(() => ({}))
    const key = (await OpenPatentAuth.get())?.userId ?? "anonymous"
    data[key] = { lastSeen: Date.now(), date: today }
    await Filesystem.writeJson(usageFilepath, data, 0o600)
  },

  async getDailyActiveUsers(): Promise<number> {
    const today = new Date().toISOString().split("T")[0]
    const data = await Filesystem.readJson<Record<string, UsageEntry>>(usageFilepath).catch(() => ({}))
    return Object.values(data).filter((entry) => entry.date === today).length
  },

  async isActiveToday(): Promise<boolean> {
    const auth = await OpenPatentAuth.get()
    if (!auth?.userId) return false

    const data = await Filesystem.readJson<Record<string, UsageEntry>>(usageFilepath).catch(() => ({}))
    const entry = data[auth.userId]
    if (!entry) return false

    const today = new Date().toISOString().split("T")[0]
    return entry.date === today
  },
}
