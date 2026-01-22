package ai.openpatent.data.remote.api

import ai.openpatent.data.model.*
import retrofit2.http.*

interface AuthApi {
    
    @POST("api/auth/register/")
    suspend fun register(@Body request: RegisterRequest): AuthResponse
    
    @POST("api/auth/login/")
    suspend fun login(@Body request: LoginRequest): AuthResponse
    
    @POST("api/auth/refresh/")
    suspend fun refreshToken(@Body request: RefreshRequest): TokenResponse
    
    @GET("api/auth/me/")
    suspend fun getCurrentUser(): UserResponse
    
    @POST("api/auth/logout/")
    suspend fun logout(@Body request: LogoutRequest): MessageResponse
    
    @GET("api/auth/health/")
    suspend fun healthCheck(): MessageResponse
}
