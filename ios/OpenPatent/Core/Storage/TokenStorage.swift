import Foundation
import Security

final class TokenStorage {
    private let service = "ai.openpatent.tokens"
    
    func saveTokens(access: String, refresh: String) throws {
        try save(key: Constants.Storage.accessTokenKey, value: access)
        try save(key: Constants.Storage.refreshTokenKey, value: refresh)
    }
    
    var accessToken: String? {
        read(key: Constants.Storage.accessTokenKey)
    }
    
    var refreshToken: String? {
        read(key: Constants.Storage.refreshTokenKey)
    }
    
    var isLoggedIn: Bool {
        accessToken != nil && refreshToken != nil
    }
    
    func clearTokens() {
        delete(key: Constants.Storage.accessTokenKey)
        delete(key: Constants.Storage.refreshTokenKey)
    }
    
    private func save(key: String, value: String) throws {
        let data = Data(value.utf8)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw TokenStorageError.saveFailed(status)
        }
    }
    
    private func read(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return string
    }
    
    private func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}

enum TokenStorageError: LocalizedError {
    case saveFailed(OSStatus)
    case readFailed(OSStatus)
    
    var errorDescription: String? {
        switch self {
        case .saveFailed(let status):
            return "Failed to save token: \(status)"
        case .readFailed(let status):
            return "Failed to read token: \(status)"
        }
    }
}
