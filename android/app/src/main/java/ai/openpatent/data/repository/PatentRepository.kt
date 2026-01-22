package ai.openpatent.data.repository

import ai.openpatent.data.model.*
import ai.openpatent.data.remote.api.PatentApi
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PatentRepository @Inject constructor(
    private val patentApi: PatentApi
) {
    // ============ Agents ============
    
    suspend fun getAgents(): Result<List<Agent>> {
        return try {
            val response = patentApi.getAgents()
            Result.success(response.agents)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getPremiumAgents(): Result<List<Agent>> {
        return try {
            val response = patentApi.getPremiumAgents()
            Result.success(response.agents)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getAgentDetail(agentId: String): Result<AgentDetailResponse> {
        return try {
            val response = patentApi.getAgentDetail(agentId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun executePremiumAgent(
        agentType: String,
        task: String,
        context: Map<String, Any> = emptyMap(),
        sessionId: String? = null
    ): Result<PremiumAgentResponse> {
        return try {
            val request = PremiumAgentRequest(agentType, task, context, sessionId)
            val response = patentApi.executePremiumAgent(request)
            if (response.success) {
                Result.success(response)
            } else {
                Result.failure(Exception(response.error ?: "Agent execution failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ Quota ============
    
    suspend fun getQuotaStatus(): Result<QuotaResponse> {
        return try {
            val response = patentApi.getQuotaStatus()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ============ Sessions ============
    
    suspend fun getSessions(): Result<List<PatentSession>> {
        return try {
            val response = patentApi.getSessions()
            Result.success(response.sessions)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getSession(sessionId: String): Result<PatentSession> {
        return try {
            val response = patentApi.getSession(sessionId)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createSession(
        title: String,
        inventionTitle: String? = null,
        technology: String? = null
    ): Result<SessionResponse> {
        return try {
            val request = CreateSessionRequest(title, inventionTitle, technology)
            val response = patentApi.createSession(request)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun updateSession(
        sessionId: String,
        updates: Map<String, Any>
    ): Result<PatentSession> {
        return try {
            val response = patentApi.updateSession(sessionId, updates)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun deleteSession(sessionId: String): Result<Unit> {
        return try {
            patentApi.deleteSession(sessionId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun shareSession(sessionId: String): Result<Unit> {
        return try {
            patentApi.shareSession(sessionId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun unshareSession(sessionId: String): Result<Unit> {
        return try {
            patentApi.unshareSession(sessionId)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
