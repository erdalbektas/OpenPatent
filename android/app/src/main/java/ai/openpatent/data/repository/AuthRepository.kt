package ai.openpatent.data.repository

import ai.openpatent.data.local.SecureTokenStorage
import ai.openpatent.data.model.*
import ai.openpatent.data.remote.api.AuthApi
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStorage: SecureTokenStorage
) {
    val isLoggedIn: Flow<Boolean> = tokenStorage.isLoggedIn
    
    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = authApi.login(LoginRequest(email, password))
            tokenStorage.saveTokens(response.access, response.refresh)
            Result.success(response.user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun register(email: String, password: String, username: String? = null): Result<User> {
        return try {
            val response = authApi.register(RegisterRequest(email, password, username))
            tokenStorage.saveTokens(response.access, response.refresh)
            Result.success(response.user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCurrentUser(): Result<UserResponse> {
        return try {
            val user = authApi.getCurrentUser()
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(): Result<String> {
        return try {
            val refreshToken = tokenStorage.getRefreshTokenSync()
                ?: return Result.failure(Exception("No refresh token"))
            
            val response = authApi.refreshToken(RefreshRequest(refreshToken))
            tokenStorage.updateAccessToken(response.access)
            response.refresh?.let { tokenStorage.saveTokens(response.access, it) }
            
            Result.success(response.access)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout(): Result<Unit> {
        return try {
            val refreshToken = tokenStorage.getRefreshTokenSync()
            if (refreshToken != null) {
                try {
                    authApi.logout(LogoutRequest(refreshToken))
                } catch (e: Exception) {
                    // Ignore logout API errors, still clear local tokens
                }
            }
            tokenStorage.clearTokens()
            Result.success(Unit)
        } catch (e: Exception) {
            tokenStorage.clearTokens()
            Result.success(Unit)
        }
    }
    
    fun isAuthenticated(): Boolean {
        return tokenStorage.getAccessTokenSync() != null
    }
}
