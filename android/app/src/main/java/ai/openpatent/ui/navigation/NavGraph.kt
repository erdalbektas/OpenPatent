package ai.openpatent.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.navArgument
import ai.openpatent.ui.auth.AuthViewModel
import ai.openpatent.ui.auth.LoginScreen
import ai.openpatent.ui.auth.RegisterScreen
import ai.openpatent.ui.components.BottomNavBar
import ai.openpatent.ui.home.HomeScreen
import ai.openpatent.ui.sessions.SessionsListScreen
import ai.openpatent.ui.sessions.SessionDetailScreen
import ai.openpatent.ui.agents.AgentsListScreen
import ai.openpatent.ui.agents.AgentDetailScreen
import ai.openpatent.ui.agents.AgentExecuteScreen
import ai.openpatent.ui.orchestrator.OrchestratorScreen
import ai.openpatent.ui.orchestrator.ThinkingLogScreen
import ai.openpatent.ui.billing.BillingScreen
import ai.openpatent.ui.settings.SettingsScreen

@Composable
fun NavGraph(
    navController: NavHostController,
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val isLoggedIn by authViewModel.isLoggedIn.collectAsState(initial = false)
    val startDestination = if (isLoggedIn) Screen.Home.route else Screen.Login.route
    
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    
    // Routes that should show bottom navigation
    val bottomNavRoutes = listOf(
        Screen.Home.route,
        Screen.Sessions.route,
        Screen.Agents.route,
        Screen.Settings.route
    )
    
    val showBottomNav = currentRoute in bottomNavRoutes
    
    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                BottomNavBar(
                    navController = navController,
                    currentRoute = currentRoute
                )
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier.padding(paddingValues)
        ) {
            // Auth screens
            composable(Screen.Login.route) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = {
                        navController.navigate(Screen.Register.route)
                    }
                )
            }
            
            composable(Screen.Register.route) {
                RegisterScreen(
                    onRegisterSuccess = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToLogin = {
                        navController.popBackStack()
                    }
                )
            }
            
            // Home
            composable(Screen.Home.route) {
                HomeScreen(
                    onNavigateToSessions = { navController.navigate(Screen.Sessions.route) },
                    onNavigateToAgents = { navController.navigate(Screen.Agents.route) },
                    onNavigateToOrchestrator = { navController.navigate(Screen.Orchestrator.route) },
                    onNavigateToBilling = { navController.navigate(Screen.Billing.route) }
                )
            }
            
            // Sessions
            composable(Screen.Sessions.route) {
                SessionsListScreen(
                    onSessionClick = { sessionId ->
                        navController.navigate(Screen.SessionDetail.createRoute(sessionId))
                    },
                    onCreateSession = { /* Handle in ViewModel */ }
                )
            }
            
            composable(
                route = Screen.SessionDetail.route,
                arguments = listOf(navArgument("sessionId") { type = NavType.StringType })
            ) { backStackEntry ->
                val sessionId = backStackEntry.arguments?.getString("sessionId") ?: return@composable
                SessionDetailScreen(
                    sessionId = sessionId,
                    onBack = { navController.popBackStack() },
                    onRunAgent = { agentId ->
                        navController.navigate(Screen.AgentExecute.createRoute(agentId))
                    }
                )
            }
            
            // Agents
            composable(Screen.Agents.route) {
                AgentsListScreen(
                    onAgentClick = { agentId ->
                        navController.navigate(Screen.AgentDetail.createRoute(agentId))
                    }
                )
            }
            
            composable(
                route = Screen.AgentDetail.route,
                arguments = listOf(navArgument("agentId") { type = NavType.StringType })
            ) { backStackEntry ->
                val agentId = backStackEntry.arguments?.getString("agentId") ?: return@composable
                AgentDetailScreen(
                    agentId = agentId,
                    onBack = { navController.popBackStack() },
                    onExecute = {
                        navController.navigate(Screen.AgentExecute.createRoute(agentId))
                    }
                )
            }
            
            composable(
                route = Screen.AgentExecute.route,
                arguments = listOf(navArgument("agentId") { type = NavType.StringType })
            ) { backStackEntry ->
                val agentId = backStackEntry.arguments?.getString("agentId") ?: return@composable
                AgentExecuteScreen(
                    agentId = agentId,
                    onBack = { navController.popBackStack() }
                )
            }
            
            // Orchestrator
            composable(Screen.Orchestrator.route) {
                OrchestratorScreen(
                    onViewThinkingLog = { sessionId ->
                        navController.navigate(Screen.ThinkingLog.createRoute(sessionId))
                    },
                    onBack = { navController.popBackStack() }
                )
            }
            
            composable(
                route = Screen.ThinkingLog.route,
                arguments = listOf(navArgument("sessionId") { type = NavType.StringType })
            ) { backStackEntry ->
                val sessionId = backStackEntry.arguments?.getString("sessionId") ?: return@composable
                ThinkingLogScreen(
                    sessionId = sessionId,
                    onBack = { navController.popBackStack() }
                )
            }
            
            // Billing
            composable(Screen.Billing.route) {
                BillingScreen(
                    onBack = { navController.popBackStack() }
                )
            }
            
            // Settings
            composable(Screen.Settings.route) {
                SettingsScreen(
                    onLogout = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(0) { inclusive = true }
                        }
                    }
                )
            }
        }
    }
}
