import Foundation

final class SettingsStorage {
    private let defaults = UserDefaults.standard
    
    var serverURL: String {
        get {
            defaults.string(forKey: Constants.Storage.serverURLKey) ?? Constants.API.defaultServerURL
        }
        set {
            defaults.set(newValue, forKey: Constants.Storage.serverURLKey)
        }
    }
    
    var userEmail: String? {
        get { defaults.string(forKey: Constants.Storage.userEmailKey) }
        set { defaults.set(newValue, forKey: Constants.Storage.userEmailKey) }
    }
    
    var userName: String? {
        get { defaults.string(forKey: Constants.Storage.userNameKey) }
        set { defaults.set(newValue, forKey: Constants.Storage.userNameKey) }
    }
    
    var quotaTier: String? {
        get { defaults.string(forKey: Constants.Storage.quotaTierKey) }
        set { defaults.set(newValue, forKey: Constants.Storage.quotaTierKey) }
    }
    
    func clearAll() {
        defaults.removeObject(forKey: Constants.Storage.serverURLKey)
        defaults.removeObject(forKey: Constants.Storage.userEmailKey)
        defaults.removeObject(forKey: Constants.Storage.userNameKey)
        defaults.removeObject(forKey: Constants.Storage.quotaTierKey)
    }
}
