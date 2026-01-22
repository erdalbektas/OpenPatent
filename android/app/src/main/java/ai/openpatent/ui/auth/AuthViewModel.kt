package ai.openpatent.ui.auth

import ai.openpatent.data.local.SecureTokenStorage
import ai.openpatent.data.local.SettingsStorage
import ai.openpatent.data.model.User
import ai.openpatent.data.repository.AuthRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val user: User? = null
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val settingsStorage: SettingsStorage,
    private val tokenStorage: SecureTokenStorage
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    val isLoggedIn: Flow<Boolean> = tokenStorage.isLoggedIn

    fun login(email: String, password: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            authRepository.login(email, password)
                .onSuccess { user ->
                    settingsStorage.setUserInfo(
                        id = user.id.toString(),
                        email = user.email,
                        tier = user.subscriptionTier
                    )
                    _uiState.update { it.copy(isLoading = false, user = user) }
                    onSuccess()
                }
                .onFailure { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Login failed"
                        ) 
                    }
                }
        }
    }

    fun register(email: String, password: String, username: String? = null, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            authRepository.register(email, password, username)
                .onSuccess { user ->
                    settingsStorage.setUserInfo(
                        id = user.id.toString(),
                        email = user.email,
                        tier = user.subscriptionTier
                    )
                    _uiState.update { it.copy(isLoading = false, user = user) }
                    onSuccess()
                }
                .onFailure { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message ?: "Registration failed"
                        ) 
                    }
                }
        }
    }

    fun logout(onComplete: () -> Unit) {
        viewModelScope.launch {
            authRepository.logout()
            settingsStorage.clearUserInfo()
            onComplete()
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
