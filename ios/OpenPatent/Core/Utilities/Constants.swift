import Foundation

enum Constants {
    enum API {
        static let defaultServerURL = "http://localhost:8000"
        static let defaultTimeout: TimeInterval = 30
        static let tokenRefreshThreshold: TimeInterval = 300 // 5 minutes
    }
    
    enum Storage {
        static let accessTokenKey = "accessToken"
        static let refreshTokenKey = "refreshToken"
        static let serverURLKey = "serverURL"
        static let userEmailKey = "userEmail"
        static let userNameKey = "userName"
        static let quotaTierKey = "quotaTier"
    }
    
    enum UI {
        static let cornerRadius: CGFloat = 12
        static let smallCornerRadius: CGFloat = 8
        static let padding: CGFloat = 16
        static let smallPadding: CGFloat = 8
        static let largePadding: CGFloat = 24
        static let buttonHeight: CGFloat = 50
        static let inputHeight: CGFloat = 56
    }
}
