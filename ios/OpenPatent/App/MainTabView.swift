import SwiftUI

struct MainTabView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)
            
            SessionsListView()
                .tabItem {
                    Label("Sessions", systemImage: "doc.text")
                }
                .tag(1)
            
            AgentsListView()
                .tabItem {
                    Label("Agents", systemImage: "sparkles")
                }
                .tag(2)
            
            OrchestratorView()
                .tabItem {
                    Label("Orchestrator", systemImage: "arrow.triangle.2.circlepath")
                }
                .tag(3)
            
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gearshape")
                }
                .tag(4)
        }
    }
}
