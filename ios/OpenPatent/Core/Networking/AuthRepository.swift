import Foundation

protocol AuthRepositoryProtocol {
    func login(email: String, password: String) async throws -> AuthResponse
    func register(email: String, password: String, username: String?) async throws -> AuthResponse
    func refreshToken(_ refresh: String) async throws -> TokenResponse
    func logout() async throws
    func getCurrentUser() async throws -> UserResponse
}

final class AuthRepository: AuthRepositoryProtocol {
    private let api: ApiClientProtocol
    
    init(api: ApiClientProtocol) {
        self.api = api
    }
    
    func login(email: String, password: String) async throws -> AuthResponse {
        try await api.request(.login, body: LoginRequest(email: email, password: password))
    }
    
    func register(email: String, password: String, username: String?) async throws -> AuthResponse {
        try await api.request(.register, body: RegisterRequest(email: email, password: password, username: username))
    }
    
    func refreshToken(_ refresh: String) async throws -> TokenResponse {
        struct RefreshRequest: Encodable {
            let refresh: String
        }
        let response: TokenResponse = try await api.request(.refreshToken, body: RefreshRequest(refresh: refresh))
        return response
    }
    
    func logout() async throws {
        let _: EmptyResponse = try await api.request(.logout, body: nil)
    }
    
    func getCurrentUser() async throws -> UserResponse {
        try await api.request(.getMe, body: nil)
    }
}

private struct EmptyResponse: Decodable {}
