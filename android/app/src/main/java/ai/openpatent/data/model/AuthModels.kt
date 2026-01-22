package ai.openpatent.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// ============ Request Models ============

@JsonClass(generateAdapter = true)
data class LoginRequest(
    val email: String,
    val password: String
)

@JsonClass(generateAdapter = true)
data class RegisterRequest(
    val email: String,
    val password: String,
    val username: String? = null
)

@JsonClass(generateAdapter = true)
data class RefreshRequest(
    val refresh: String
)

@JsonClass(generateAdapter = true)
data class LogoutRequest(
    val refresh: String
)

// ============ Response Models ============

@JsonClass(generateAdapter = true)
data class AuthResponse(
    val user: User,
    val access: String,
    val refresh: String
)

@JsonClass(generateAdapter = true)
data class TokenResponse(
    val access: String,
    val refresh: String? = null
)

@JsonClass(generateAdapter = true)
data class User(
    val id: Int,
    val email: String,
    val username: String,
    @Json(name = "subscription_tier") val subscriptionTier: String = "free",
    @Json(name = "requests_per_hour") val requestsPerHour: Int = 100,
    @Json(name = "tokens_per_hour") val tokensPerHour: Int = 100000,
    @Json(name = "created_at") val createdAt: String? = null
)

@JsonClass(generateAdapter = true)
data class UserResponse(
    val id: Int,
    val email: String,
    val username: String,
    @Json(name = "subscription_tier") val subscriptionTier: String = "free",
    @Json(name = "requests_per_hour") val requestsPerHour: Int = 100,
    @Json(name = "tokens_per_hour") val tokensPerHour: Int = 100000,
    @Json(name = "created_at") val createdAt: String? = null
)

@JsonClass(generateAdapter = true)
data class MessageResponse(
    val message: String? = null,
    val error: String? = null
)

@JsonClass(generateAdapter = true)
data class ErrorResponse(
    val error: String? = null,
    val message: String? = null,
    val detail: String? = null
)
