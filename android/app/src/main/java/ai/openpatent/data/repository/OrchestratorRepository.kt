package ai.openpatent.data.repository

import ai.openpatent.data.model.*
import ai.openpatent.data.remote.api.OrchestratorApi
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OrchestratorRepository @Inject constructor(
    private val orchestratorApi: OrchestratorApi
) {
    suspend fun createPlan(
        request: String,
        technology: String = "software",
        sessionId: String? = null
    ): Result<OrchestratorPlan> {
        return try {
            val planRequest = OrchestratorPlanRequest(request, technology, sessionId)
            val response = orchestratorApi.createPlan(planRequest)
            if (response.success && response.plan != null) {
                Result.success(response.plan)
            } else {
                Result.failure(Exception(response.error ?: "Failed to create plan"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun executePlan(
        request: String,
        technology: String = "software",
        sessionId: String? = null,
        planId: String? = null
    ): Result<OrchestratorExecuteResponse> {
        return try {
            val execRequest = OrchestratorExecuteRequest(request, technology, sessionId, planId)
            val response = orchestratorApi.executePlan(execRequest)
            if (response.success) {
                Result.success(response)
            } else {
                Result.failure(Exception(response.error ?: "Failed to execute plan"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getTemplates(): Result<List<OrchestratorTemplate>> {
        return try {
            val response = orchestratorApi.getTemplates()
            Result.success(response.templates)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getThinkingLog(sessionId: String): Result<ThinkingLogResponse> {
        return try {
            val response = orchestratorApi.getThinkingLog(sessionId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
