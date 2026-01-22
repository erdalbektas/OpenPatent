import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @StateObject private var viewModel = HomeViewModel()
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: Constants.UI.padding) {
                    quotaSection
                    
                    quickActionsSection
                    
                    recentSessionsSection
                }
                .padding()
            }
            .navigationTitle("Home")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        // Navigate to settings
                    } label: {
                        Image(systemName: "gearshape")
                    }
                }
            }
            .refreshable {
                await viewModel.refresh()
            }
            .overlay {
                if viewModel.isLoading {
                    LoadingView(message: "Loading...")
                }
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
    }
    
    private var quotaSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Your Quota")
                .font(.headline)
            
            if viewModel.quotaInfo.isEmpty {
                Text("No quota information available")
                    .foregroundStyle(.secondary)
            } else {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Constants.UI.smallPadding) {
                    ForEach(Array(viewModel.quotaInfo.keys.sorted()), id: \.self) { key in
                        if let info = viewModel.quotaInfo[key] {
                            QuotaStatusCard(
                                tier: viewModel.tier,
                                used: info.used,
                                limit: info.limit
                            )
                        }
                    }
                }
            }
        }
    }
    
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Quick Actions")
                .font(.headline)
            
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Constants.UI.smallPadding) {
                QuickActionCard(
                    icon: "plus.circle",
                    title: "New Session",
                    color: .blue
                ) {
                    Task {
                        await viewModel.createSession()
                    }
                }
                
                QuickActionCard(
                    icon: "sparkles",
                    title: "Run Agent",
                    color: .purple
                ) {
                    // Navigate to agents
                }
                
                QuickActionCard(
                    icon: "arrow.triangle.2.circlepath",
                    title: "Orchestrator",
                    color: .orange
                ) {
                    // Navigate to orchestrator
                }
                
                QuickActionCard(
                    icon: "creditcard",
                    title: "Billing",
                    color: .green
                ) {
                    // Navigate to billing
                }
            }
        }
    }
    
    private var recentSessionsSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            HStack {
                Text("Recent Sessions")
                    .font(.headline)
                Spacer()
                Button("See All") {
                    // Navigate to sessions
                }
                .font(.subheadline)
            }
            
            if viewModel.recentSessions.isEmpty {
                EmptyStateView(
                    icon: "doc.text",
                    title: "No Sessions Yet",
                    message: "Create your first patent session to get started",
                    actionTitle: "Create Session"
                ) {
                    Task {
                        await viewModel.createSession()
                    }
                }
            } else {
                ForEach(viewModel.recentSessions) { session in
                    SessionCard(session: session)
                }
            }
        }
    }
}

struct QuickActionCard: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: Constants.UI.smallPadding) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 100)
            .background(Color(.systemGray6))
            .cornerRadius(Constants.UI.cornerRadius)
        }
        .buttonStyle(.plain)
    }
}

@MainActor
final class HomeViewModel: ObservableObject {
    @Published var isLoading: Bool = true
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    @Published var tier: String = "free"
    @Published var quotaInfo: [String: QuotaResponse.QuotaInfo] = [:]
    @Published var recentSessions: [PatentSession] = []
    
    private let patentRepository: PatentRepositoryProtocol
    
    init(patentRepository: PatentRepositoryProtocol? = nil) {
        let tokenStorage = TokenStorage()
        let settingsStorage = SettingsStorage()
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        self.patentRepository = patentRepository ?? PatentRepository(api: apiClient)
    }
    
    func loadData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            async let sessionsResult = patentRepository.getSessions()
            async let quotaResult = patentRepository.getQuota()
            
            let (sessions, quota) = try await (sessionsResult, quotaResult)
            
            recentSessions = Array(sessions.prefix(5))
            tier = quota.tier
            quotaInfo = quota.quotas
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
    
    func refresh() async {
        await loadData()
    }
    
    func createSession() async {
        do {
            let session = try await patentRepository.createSession(title: "New Patent Session")
            recentSessions.insert(session, at: 0)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
