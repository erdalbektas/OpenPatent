package ai.openpatent.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// ============ Session Models ============

@JsonClass(generateAdapter = true)
data class PatentSession(
    val id: String,
    val title: String,
    @Json(name = "invention_title") val inventionTitle: String? = null,
    @Json(name = "invention_summary") val inventionSummary: String? = null,
    val technology: String? = null,
    val status: String = "draft",
    val claims: List<String> = emptyList(),
    val specification: Map<String, String> = emptyMap(),
    @Json(name = "prior_art") val priorArt: List<PriorArt> = emptyList(),
    @Json(name = "office_actions") val officeActions: List<String> = emptyList(),
    @Json(name = "is_premium") val isPremium: Boolean = false,
    @Json(name = "created_at") val createdAt: String? = null,
    @Json(name = "updated_at") val updatedAt: String? = null
)

@JsonClass(generateAdapter = true)
data class PriorArt(
    val id: String? = null,
    val title: String,
    val source: String,
    val url: String? = null,
    @Json(name = "relevance_score") val relevanceScore: Double = 0.0,
    val summary: String? = null
)

@JsonClass(generateAdapter = true)
data class SessionsListResponse(
    val sessions: List<PatentSession>,
    val total: Int? = null
)

@JsonClass(generateAdapter = true)
data class SessionResponse(
    val session: PatentSession? = null,
    val id: String? = null,
    val title: String? = null
)

@JsonClass(generateAdapter = true)
data class CreateSessionRequest(
    val title: String,
    @Json(name = "invention_title") val inventionTitle: String? = null,
    val technology: String? = null
)

// ============ Agent Models ============

@JsonClass(generateAdapter = true)
data class Agent(
    val id: String,
    val name: String,
    val description: String = "",
    val type: String = "local", // "local" or "premium"
    val category: String = "general",
    val icon: String? = null,
    val color: String? = null,
    @Json(name = "is_premium") val isPremium: Boolean = false,
    @Json(name = "quota_limit") val quotaLimit: Int? = null,
    @Json(name = "quota_used") val quotaUsed: Int? = null,
    val tags: List<String> = emptyList()
)

@JsonClass(generateAdapter = true)
data class AgentsListResponse(
    val agents: List<Agent>
)

@JsonClass(generateAdapter = true)
data class AgentDetailResponse(
    val agent: Agent,
    val versions: List<AgentVersion>? = null,
    @Json(name = "system_prompt") val systemPrompt: String? = null
)

@JsonClass(generateAdapter = true)
data class AgentVersion(
    val version: String,
    @Json(name = "created_at") val createdAt: String,
    val changelog: String? = null
)

// ============ Premium Agent Execution ============

@JsonClass(generateAdapter = true)
data class PremiumAgentRequest(
    @Json(name = "agent_type") val agentType: String,
    val task: String,
    val context: Map<String, Any> = emptyMap(),
    @Json(name = "session_id") val sessionId: String? = null
)

@JsonClass(generateAdapter = true)
data class PremiumAgentResponse(
    val success: Boolean,
    val result: AgentResult? = null,
    val error: String? = null,
    @Json(name = "tokens_used") val tokensUsed: Int? = null,
    val cost: Double? = null,
    @Json(name = "quota_remaining") val quotaRemaining: Int? = null
)

@JsonClass(generateAdapter = true)
data class AgentResult(
    val content: String? = null,
    val data: Map<String, Any>? = null,
    @Json(name = "structured_output") val structuredOutput: Map<String, Any>? = null
)

// ============ Quota Models ============

@JsonClass(generateAdapter = true)
data class QuotaResponse(
    val tier: String,
    val quotas: Map<String, QuotaInfo>,
    @Json(name = "reset_date") val resetDate: String? = null
)

@JsonClass(generateAdapter = true)
data class QuotaInfo(
    val used: Int,
    val limit: Int,
    val remaining: Int
)
