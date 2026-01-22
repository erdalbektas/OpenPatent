package ai.openpatent.ui.home

import ai.openpatent.data.model.PatentSession
import ai.openpatent.data.model.QuotaInfo
import ai.openpatent.data.repository.PatentRepository
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val recentSessions: List<PatentSession> = emptyList(),
    val quotaTier: String = "free",
    val quotas: Map<String, QuotaInfo> = emptyMap(),
    val resetDate: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val patentRepository: PatentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Load sessions and quota in parallel
            val sessionsResult = patentRepository.getSessions()
            val quotaResult = patentRepository.getQuotaStatus()
            
            _uiState.update { state ->
                state.copy(
                    isLoading = false,
                    recentSessions = sessionsResult.getOrNull()?.take(5) ?: emptyList(),
                    quotaTier = quotaResult.getOrNull()?.tier ?: "free",
                    quotas = quotaResult.getOrNull()?.quotas ?: emptyMap(),
                    resetDate = quotaResult.getOrNull()?.resetDate,
                    error = sessionsResult.exceptionOrNull()?.message 
                        ?: quotaResult.exceptionOrNull()?.message
                )
            }
        }
    }

    fun refresh() {
        loadData()
    }
}
