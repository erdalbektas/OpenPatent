import Foundation

final class ServiceLocator {
    static let shared = ServiceLocator()
    
    private var services: [String: Any] = [:]
    
    private init() {}
    
    func register<T>(_ type: T.Type, factory: @escaping () -> T) {
        let key = String(describing: type)
        services[key] = factory
    }
    
    func resolve<T>(_ type: T.Type) -> T? {
        let key = String(describing: type)
        guard let factory = services[key] as? () -> T else {
            return nil
        }
        return factory()
    }
    
    func registerSingleton<T>(_ instance: T, for type: T.Type) {
        let key = String(describing: type)
        services[key] = { instance }
    }
    
    func reset() {
        services.removeAll()
    }
}

extension ServiceLocator {
    func setupDependencies() {
        let tokenStorage = TokenStorage()
        let settingsStorage = SettingsStorage()
        
        register(TokenStorage.self) { tokenStorage }
        register(SettingsStorage.self) { settingsStorage }
        
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        register(ApiClientProtocol.self) { apiClient }
        
        register(AuthRepositoryProtocol.self) {
            AuthRepository(api: self.resolve(ApiClientProtocol.self)!)
        }
        
        register(PatentRepositoryProtocol.self) {
            PatentRepository(api: self.resolve(ApiClientProtocol.self)!)
        }
        
        register(OrchestratorRepositoryProtocol.self) {
            OrchestratorRepository(api: self.resolve(ApiClientProtocol.self)!)
        }
        
        register(BillingRepositoryProtocol.self) {
            BillingRepository(api: self.resolve(ApiClientProtocol.self)!)
        }
    }
}
