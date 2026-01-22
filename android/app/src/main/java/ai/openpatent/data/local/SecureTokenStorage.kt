package ai.openpatent.data.local

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Secure token storage using Android Keystore for encryption.
 * Stores JWT access and refresh tokens securely.
 */
@Singleton
class SecureTokenStorage @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val securePrefs = EncryptedSharedPreferences.create(
        context,
        "openpatent_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    private val _accessToken = MutableStateFlow<String?>(securePrefs.getString(KEY_ACCESS_TOKEN, null))
    private val _refreshToken = MutableStateFlow<String?>(securePrefs.getString(KEY_REFRESH_TOKEN, null))
    private val _isLoggedIn = MutableStateFlow(_accessToken.value != null)

    val accessToken: Flow<String?> = _accessToken.asStateFlow()
    val refreshToken: Flow<String?> = _refreshToken.asStateFlow()
    val isLoggedIn: Flow<Boolean> = _isLoggedIn.asStateFlow()

    fun getAccessTokenSync(): String? = _accessToken.value
    fun getRefreshTokenSync(): String? = _refreshToken.value

    fun saveTokens(accessToken: String, refreshToken: String) {
        securePrefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .apply()
        
        _accessToken.value = accessToken
        _refreshToken.value = refreshToken
        _isLoggedIn.value = true
    }

    fun updateAccessToken(accessToken: String) {
        securePrefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .apply()
        
        _accessToken.value = accessToken
    }

    fun clearTokens() {
        securePrefs.edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .apply()
        
        _accessToken.value = null
        _refreshToken.value = null
        _isLoggedIn.value = false
    }

    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
    }
}
