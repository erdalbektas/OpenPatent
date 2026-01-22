package ai.openpatent.data.remote.api

import ai.openpatent.data.model.*
import retrofit2.http.*

interface PatentApi {
    
    // ============ Agents ============
    
    @GET("api/patent/agents/")
    suspend fun getAgents(): AgentsListResponse
    
    @GET("api/patent/agents/premium/list/")
    suspend fun getPremiumAgents(): AgentsListResponse
    
    @GET("api/patent/agents/{agentId}/")
    suspend fun getAgentDetail(@Path("agentId") id: String): AgentDetailResponse
    
    @POST("api/patent/agents/premium/")
    suspend fun executePremiumAgent(@Body request: PremiumAgentRequest): PremiumAgentResponse
    
    // ============ Quota ============
    
    @GET("api/patent/quota/")
    suspend fun getQuotaStatus(): QuotaResponse
    
    // ============ Sessions ============
    
    @GET("api/patent/sessions/")
    suspend fun getSessions(): SessionsListResponse
    
    @POST("api/patent/sessions/")
    suspend fun createSession(@Body request: CreateSessionRequest): SessionResponse
    
    @GET("api/patent/sessions/{sessionId}/")
    suspend fun getSession(@Path("sessionId") id: String): PatentSession
    
    @PATCH("api/patent/sessions/{sessionId}/")
    suspend fun updateSession(
        @Path("sessionId") id: String,
        @Body updates: Map<String, Any>
    ): PatentSession
    
    @DELETE("api/patent/sessions/{sessionId}/")
    suspend fun deleteSession(@Path("sessionId") id: String): MessageResponse
    
    @POST("api/patent/sessions/{sessionId}/share/")
    suspend fun shareSession(@Path("sessionId") id: String): MessageResponse
    
    @DELETE("api/patent/sessions/{sessionId}/share/")
    suspend fun unshareSession(@Path("sessionId") id: String): MessageResponse
}
