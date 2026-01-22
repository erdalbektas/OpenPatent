package ai.openpatent.data.remote.api

import ai.openpatent.data.model.*
import retrofit2.http.*

interface OrchestratorApi {
    
    @POST("api/patent/orchestrator/plan/")
    suspend fun createPlan(@Body request: OrchestratorPlanRequest): OrchestratorPlanResponse
    
    @POST("api/patent/orchestrator/execute/")
    suspend fun executePlan(@Body request: OrchestratorExecuteRequest): OrchestratorExecuteResponse
    
    @GET("api/patent/orchestrator/templates/")
    suspend fun getTemplates(): TemplatesListResponse
    
    @GET("api/patent/orchestrator/thinking/{sessionId}/")
    suspend fun getThinkingLog(@Path("sessionId") id: String): ThinkingLogResponse
}
