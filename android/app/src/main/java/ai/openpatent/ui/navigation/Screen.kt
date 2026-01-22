package ai.openpatent.ui.navigation

sealed class Screen(val route: String) {
    // Auth
    object Login : Screen("login")
    object Register : Screen("register")
    
    // Main
    object Home : Screen("home")
    object Sessions : Screen("sessions")
    object SessionDetail : Screen("sessions/{sessionId}") {
        fun createRoute(sessionId: String) = "sessions/$sessionId"
    }
    
    // Agents
    object Agents : Screen("agents")
    object AgentDetail : Screen("agents/{agentId}") {
        fun createRoute(agentId: String) = "agents/$agentId"
    }
    object AgentExecute : Screen("agents/{agentId}/execute") {
        fun createRoute(agentId: String) = "agents/$agentId/execute"
    }
    
    // Orchestrator
    object Orchestrator : Screen("orchestrator")
    object ThinkingLog : Screen("orchestrator/thinking/{sessionId}") {
        fun createRoute(sessionId: String) = "orchestrator/thinking/$sessionId"
    }
    
    // Billing & Settings
    object Billing : Screen("billing")
    object Settings : Screen("settings")
}
