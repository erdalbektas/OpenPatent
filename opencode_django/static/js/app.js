class openpatentAPI {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl
    this.token = localStorage.getItem("access_token")
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem("access_token", token)
    } else {
      localStorage.removeItem("access_token")
    }
  }

  async request(method, endpoint, data = null) {
    const headers = {
      "Content-Type": "application/json",
    }

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }

    const options = {
      method,
      headers,
    }

    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
      options.body = JSON.stringify(data)
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options)

    if (response.status === 401) {
      this.setToken(null)
      window.location.href = "/api/auth/login/"
      throw new Error("Unauthorized")
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: "Request failed" }))
      throw new Error(error.error || error.message || "Request failed")
    }

    return response.json()
  }

  async login(email, password) {
    const data = await this.request("POST", "/api/auth/login/", { email, password })
    this.setToken(data.access)
    return data
  }

  async register(email, password, username) {
    const data = await this.request("POST", "/api/auth/register/", { email, password, username })
    this.setToken(data.access)
    return data
  }

  logout() {
    this.setToken(null)
  }

  async getUser() {
    return this.request("GET", "/api/auth/me/")
  }

  async getSessions(limit = 50, offset = 0) {
    return this.request("GET", `/api/sessions/?limit=${limit}&offset=${offset}`)
  }

  async createSession(title = "New Session") {
    return this.request("POST", "/api/sessions/", { title })
  }

  async getSession(sessionId) {
    return this.request("GET", `/api/sessions/${sessionId}/`)
  }

  async deleteSession(sessionId) {
    return this.request("DELETE", `/api/sessions/${sessionId}/`)
  }

  async shareSession(sessionId) {
    return this.request("POST", `/api/sessions/${sessionId}/share/`)
  }

  async unshareSession(sessionId) {
    return this.request("DELETE", `/api/sessions/${sessionId}/share/`)
  }

  async getSessionMessages(sessionId) {
    return this.request("GET", `/api/sessions/${sessionId}/messages/`)
  }

  async addSessionMessage(sessionId, message) {
    return this.request("POST", `/api/sessions/${sessionId}/messages/`, message)
  }

  async getUsage() {
    return this.request("GET", "/api/usage/")
  }

  async getSubscription() {
    return this.request("GET", "/billing/subscription/")
  }

  async createCheckout(priceId) {
    return this.request("POST", "/billing/checkout/", { price_id: priceId })
  }

  async createPortal() {
    return this.request("POST", "/billing/portal/")
  }

  async cancelSubscription() {
    return this.request("POST", "/billing/cancel/")
  }
}

const api = new openpatentAPI()

async function showSessions() {
  try {
    const { sessions } = await api.getSessions()

    const container = document.getElementById("sessions-container")
    if (!container) return

    if (sessions.length === 0) {
      container.innerHTML = "<p>No sessions yet. Create your first session!</p>"
      return
    }

    container.innerHTML = sessions
      .map(
        (session) => `
            <div class="card">
                <h3>${escapeHtml(session.title)}</h3>
                <p>ID: ${session.id}</p>
                <p>Created: ${new Date(session.time.created).toLocaleString()}</p>
                <button onclick="viewSession('${session.id}')">View</button>
            </div>
        `,
      )
      .join("")
  } catch (error) {
    console.error("Failed to load sessions:", error)
  }
}

async function showUsage() {
  try {
    const { usage, limits, tier } = await api.getUsage()

    const container = document.getElementById("usage-container")
    if (!container) return

    const requestsPercent = ((usage.requests_used / limits.requests_per_hour) * 100).toFixed(1)
    const tokensPercent = ((usage.tokens_used / limits.tokens_per_hour) * 100).toFixed(1)

    container.innerHTML = `
            <div class="card">
                <h3>Usage - ${tier.toUpperCase()} Plan</h3>
                <p>Resets: ${new Date(usage.reset_at).toLocaleString()}</p>
                
                <h4>Requests</h4>
                <div class="usage-bar">
                    <div class="usage-bar-fill" style="width: ${requestsPercent}%"></div>
                </div>
                <p>${usage.requests_used} / ${limits.requests_per_hour} (${requestsPercent}%)</p>
                
                <h4>Tokens</h4>
                <div class="usage-bar">
                    <div class="usage-bar-fill" style="width: ${tokensPercent}%"></div>
                </div>
                <p>${usage.tokens_used.toLocaleString()} / ${limits.tokens_per_hour.toLocaleString()} (${tokensPercent}%)</p>
            </div>
        `
  } catch (error) {
    console.error("Failed to load usage:", error)
  }
}

async function showPricing() {
  try {
    const response = await fetch("/billing/pricing/")
    const { plans } = await response.json()

    const container = document.getElementById("pricing-container")
    if (!container) return

    container.innerHTML = plans
      .map(
        (plan) => `
            <div class="plan-card ${plan.id === "pro_monthly" ? "featured" : ""}">
                <h3>${plan.name}</h3>
                <div class="plan-price">
                    ${plan.price === 0 ? "Free" : `$${(plan.price / 100).toFixed(2)}<span>/mo</span>`}
                </div>
                <ul class="plan-features">
                    <li>${plan.requests_per_hour} requests/hour</li>
                    <li>${plan.tokens_per_hour.toLocaleString()} tokens/hour</li>
                </ul>
                ${plan.price_id
            ? `
                    <button onclick="subscribe('${plan.price_id}')">
                        ${plan.price === 0 ? "Current Plan" : "Subscribe"}
                    </button>
                `
            : ""
          }
            </div>
        `,
      )
      .join("")
  } catch (error) {
    console.error("Failed to load pricing:", error)
  }
}

async function subscribe(priceId) {
  try {
    const { url } = await api.createCheckout(priceId)
    window.location.href = url
  } catch (error) {
    alert("Failed to create checkout: " + error.message)
  }
}

async function viewSession(sessionId) {
  window.location.href = `/api/sessions/${sessionId}/`
}

function escapeHtml(text) {
  const div = document.createElement("div")
  div.textContent = text
  return div.innerHTML
}

if (document.getElementById("sessions-container")) {
  showSessions()
}

if (document.getElementById("usage-container")) {
  showUsage()
}

if (document.getElementById("pricing-container")) {
  showPricing()
}
