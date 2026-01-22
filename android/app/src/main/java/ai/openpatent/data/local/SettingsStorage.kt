package ai.openpatent.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import ai.openpatent.BuildConfig
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "openpatent_settings")

/**
 * Settings storage for app configuration.
 * Uses DataStore for structured data persistence.
 */
@Singleton
class SettingsStorage @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    val serverUrl: Flow<String> = dataStore.data.map { preferences ->
        preferences[KEY_SERVER_URL] ?: BuildConfig.DEFAULT_SERVER_URL
    }

    val isDarkMode: Flow<Boolean> = dataStore.data.map { preferences ->
        preferences[KEY_DARK_MODE] ?: false
    }

    val userEmail: Flow<String?> = dataStore.data.map { preferences ->
        preferences[KEY_USER_EMAIL]
    }

    val userId: Flow<String?> = dataStore.data.map { preferences ->
        preferences[KEY_USER_ID]
    }

    val subscriptionTier: Flow<String> = dataStore.data.map { preferences ->
        preferences[KEY_SUBSCRIPTION_TIER] ?: "free"
    }

    suspend fun setServerUrl(url: String) {
        dataStore.edit { preferences ->
            preferences[KEY_SERVER_URL] = url.trimEnd('/')
        }
    }

    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[KEY_DARK_MODE] = enabled
        }
    }

    suspend fun setUserInfo(id: String, email: String, tier: String) {
        dataStore.edit { preferences ->
            preferences[KEY_USER_ID] = id
            preferences[KEY_USER_EMAIL] = email
            preferences[KEY_SUBSCRIPTION_TIER] = tier
        }
    }

    suspend fun clearUserInfo() {
        dataStore.edit { preferences ->
            preferences.remove(KEY_USER_ID)
            preferences.remove(KEY_USER_EMAIL)
            preferences.remove(KEY_SUBSCRIPTION_TIER)
        }
    }

    companion object {
        private val KEY_SERVER_URL = stringPreferencesKey("server_url")
        private val KEY_DARK_MODE = booleanPreferencesKey("dark_mode")
        private val KEY_USER_EMAIL = stringPreferencesKey("user_email")
        private val KEY_USER_ID = stringPreferencesKey("user_id")
        private val KEY_SUBSCRIPTION_TIER = stringPreferencesKey("subscription_tier")
    }
}
