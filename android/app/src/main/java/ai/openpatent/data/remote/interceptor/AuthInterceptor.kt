package ai.openpatent.data.remote.interceptor

import ai.openpatent.data.local.SecureTokenStorage
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

/**
 * OkHttp interceptor that adds JWT Authorization header to requests.
 */
class AuthInterceptor @Inject constructor(
    private val tokenStorage: SecureTokenStorage
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Skip auth for public endpoints
        val path = originalRequest.url.encodedPath
        if (isPublicEndpoint(path)) {
            return chain.proceed(originalRequest)
        }

        val accessToken = tokenStorage.getAccessTokenSync()
        
        return if (accessToken != null) {
            val authenticatedRequest = originalRequest.newBuilder()
                .header("Authorization", "Bearer $accessToken")
                .build()
            chain.proceed(authenticatedRequest)
        } else {
            chain.proceed(originalRequest)
        }
    }

    private fun isPublicEndpoint(path: String): Boolean {
        return path.contains("/auth/login") ||
               path.contains("/auth/register") ||
               path.contains("/auth/refresh") ||
               path.contains("/billing/pricing") ||
               path.contains("/health")
    }
}
