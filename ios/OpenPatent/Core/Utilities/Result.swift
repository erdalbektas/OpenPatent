import Foundation

enum AppError: LocalizedError {
    case networkError(Error)
    case decodingError(Error)
    case unauthorized
    case notFound
    case serverError(Int, String)
    case invalidURL
    case noData
    case tokenExpired
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Failed to process response: \(error.localizedDescription)"
        case .unauthorized:
            return "Session expired. Please log in again."
        case .notFound:
            return "Resource not found."
        case .serverError(let code, let message):
            return "Server error (\(code)): \(message)"
        case .invalidURL:
            return "Invalid URL."
        case .noData:
            return "No data received."
        case .tokenExpired:
            return "Your session has expired. Please log in again."
        case .unknown:
            return "An unknown error occurred."
        }
    }
}
