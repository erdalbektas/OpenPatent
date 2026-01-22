import Foundation
import SwiftUI

enum Route: Hashable {
    case login
    case register
    case home
    case sessions
    case sessionDetail(sessionId: String)
    case agents
    case agentDetail(agentId: String)
    case agentExecute(agentId: String)
    case orchestrator
    case billing
    case settings
}

@MainActor
final class AppCoordinator: ObservableObject {
    @Published var isAuthenticated: Bool = false
    @Published var currentRoute: Route?
    
    private let tokenStorage: TokenStorage
    private let settingsStorage: SettingsStorage
    private let authRepository: AuthRepositoryProtocol
    private let patentRepository: PatentRepositoryProtocol
    
    init(
        tokenStorage: TokenStorage = TokenStorage(),
        settingsStorage: SettingsStorage = SettingsStorage(),
        authRepository: AuthRepositoryProtocol? = nil,
        patentRepository: PatentRepositoryProtocol? = nil
    ) {
        self.tokenStorage = tokenStorage
        self.settingsStorage = settingsStorage
        
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        self.authRepository = authRepository ?? AuthRepository(api: apiClient)
        self.patentRepository = patentRepository ?? PatentRepository(api: apiClient)
        
        self.isAuthenticated = tokenStorage.isLoggedIn
    }
    
    func login(email: String, password: String) async throws {
        let response = try await authRepository.login(email: email, password: password)
        try tokenStorage.saveTokens(access: response.access, refresh: response.refresh)
        settingsStorage.userEmail = response.user.email
        settingsStorage.userName = response.user.username
        isAuthenticated = true
    }
    
    func register(email: String, password: String, username: String?) async throws {
        let response = try await authRepository.register(email: email, password: password, username: username)
        try tokenStorage.saveTokens(access: response.access, refresh: response.refresh)
        settingsStorage.userEmail = response.user.email
        settingsStorage.userName = response.user.username
        isAuthenticated = true
    }
    
    func logout() async {
        try? await authRepository.logout()
        tokenStorage.clearTokens()
        settingsStorage.clearAll()
        isAuthenticated = false
    }
}
