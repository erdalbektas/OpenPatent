import Foundation

protocol ApiClientProtocol {
    func request<T: Decodable>(_ endpoint: Endpoint, body: Encodable?) async throws -> T
    func requestData(_ endpoint: Endpoint, body: Encodable?) async throws -> Data
}

final class ApiClient: ApiClientProtocol {
    private let session: URLSession
    private let tokenStorage: TokenStorage
    private let settingsStorage: SettingsStorage
    
    init(session: URLSession = .shared, tokenStorage: TokenStorage, settingsStorage: SettingsStorage) {
        self.session = session
        self.tokenStorage = tokenStorage
        self.settingsStorage = settingsStorage
    }
    
    var baseURL: String {
        settingsStorage.serverURL
    }
    
    func request<T: Decodable>(_ endpoint: Endpoint, body: Encodable? = nil) async throws -> T {
        let data = try await requestData(endpoint, body: body)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }
    
    func requestData(_ endpoint: Endpoint, body: Encodable? = nil) async throws -> Data {
        let url = try buildURL(for: endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        if endpoint.requiresAuth, let token = tokenStorage.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppError.unknown
        }
        
        try validateResponse(httpResponse, data: data)
        
        return data
    }
    
    func requestWithRefresh<T: Decodable>(_ endpoint: Endpoint, body: Encodable? = nil) async throws -> T {
        do {
            return try await request(endpoint, body: body)
        } catch AppError.unauthorized {
            if try await refreshToken() {
                return try await request(endpoint, body: body)
            }
            throw AppError.tokenExpired
        }
    }
    
    private func buildURL(for endpoint: Endpoint) throws -> URL {
        guard let url = URL(string: baseURL + endpoint.path) else {
            throw AppError.invalidURL
        }
        return url
    }
    
    private func validateResponse(_ response: HTTPURLResponse, data: Data) throws {
        switch response.statusCode {
        case 200...299:
            return
        case 401:
            throw AppError.unauthorized
        case 404:
            throw AppError.notFound
        case 400...499:
            let message = extractErrorMessage(from: data)
            throw AppError.serverError(response.statusCode, message)
        case 500...599:
            let message = extractErrorMessage(from: data)
            throw AppError.serverError(response.statusCode, message)
        default:
            throw AppError.unknown
        }
    }
    
    private func extractErrorMessage(from data: Data) -> String {
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let message = json["detail"] as? String ?? json["error"] as? String {
            return message
        }
        return "Unknown error"
    }
    
    private func refreshToken() async throws -> Bool {
        guard let refreshToken = tokenStorage.refreshToken else {
            return false
        }
        
        struct RefreshRequest: Encodable {
            let refresh: String
        }
        
        struct RefreshResponse: Decodable {
            let access: String
            let refresh: String
        }
        
        do {
            let response: RefreshResponse = try await request(.refreshToken, body: RefreshRequest(refresh: refreshToken))
            try tokenStorage.saveTokens(access: response.access, refresh: response.refresh)
            return true
        } catch {
            tokenStorage.clearTokens()
            return false
        }
    }
}
