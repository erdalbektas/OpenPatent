import SwiftUI

@main
struct OpenPatentApp: App {
    @StateObject private var appCoordinator = AppCoordinator()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appCoordinator)
        }
    }
}

struct ContentView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    
    var body: some View {
        Group {
            if coordinator.isAuthenticated {
                MainTabView()
            } else {
                AuthNavigationView()
            }
        }
        .animation(.easeInOut, value: coordinator.isAuthenticated)
    }
}
