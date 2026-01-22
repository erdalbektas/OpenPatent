package ai.openpatent.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// ============ Plan Request ============

@JsonClass(generateAdapter = true)
data class OrchestratorPlanRequest(
    val request: String,
    val technology: String = "software",
    @Json(name = "session_id") val sessionId: String? = null
)

// ============ Plan Response ============

@JsonClass(generateAdapter = true)
data class OrchestratorPlanResponse(
    val success: Boolean,
    val plan: OrchestratorPlan? = null,
    val error: String? = null
)

@JsonClass(generateAdapter = true)
data class OrchestratorPlan(
    val id: String,
    val goal: String,
    val steps: List<OrchestratorStep>,
    val technology: String,
    @Json(name = "estimated_cost") val estimatedCost: Double? = null,
    @Json(name = "estimated_time") val estimatedTime: String? = null,
    val status: String = "pending"
)

@JsonClass(generateAdapter = true)
data class OrchestratorStep(
    val id: String,
    val order: Int,
    @Json(name = "agent_type") val agentType: String,
    @Json(name = "agent_name") val agentName: String,
    val task: String,
    val description: String? = null,
    val status: String = "pending",
    val result: String? = null,
    @Json(name = "depends_on") val dependsOn: List<String> = emptyList()
)

// ============ Execute Request ============

@JsonClass(generateAdapter = true)
data class OrchestratorExecuteRequest(
    val request: String,
    val technology: String = "software",
    @Json(name = "session_id") val sessionId: String? = null,
    @Json(name = "plan_id") val planId: String? = null
)

// ============ Execute Response ============

@JsonClass(generateAdapter = true)
data class OrchestratorExecuteResponse(
    val success: Boolean,
    @Json(name = "session_id") val sessionId: String? = null,
    val results: List<StepResult>? = null,
    val plan: OrchestratorPlan? = null,
    val error: String? = null
)

@JsonClass(generateAdapter = true)
data class StepResult(
    @Json(name = "step_id") val stepId: String,
    @Json(name = "agent_type") val agentType: String,
    val status: String,
    val result: String? = null,
    val error: String? = null
)

// ============ Templates ============

@JsonClass(generateAdapter = true)
data class TemplatesListResponse(
    val templates: List<OrchestratorTemplate>
)

@JsonClass(generateAdapter = true)
data class OrchestratorTemplate(
    val id: String,
    val name: String,
    val description: String,
    val technology: String,
    val steps: List<TemplateStep>,
    @Json(name = "example_prompt") val examplePrompt: String? = null
)

@JsonClass(generateAdapter = true)
data class TemplateStep(
    val order: Int,
    @Json(name = "agent_type") val agentType: String,
    val description: String
)

// ============ Thinking Log ============

@JsonClass(generateAdapter = true)
data class ThinkingLogResponse(
    @Json(name = "session_id") val sessionId: String,
    val entries: List<ThinkingEntry>
)

@JsonClass(generateAdapter = true)
data class ThinkingEntry(
    val timestamp: String,
    val type: String, // "thinking", "action", "result"
    val content: String,
    @Json(name = "agent_type") val agentType: String? = null
)
