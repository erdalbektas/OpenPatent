import SwiftUI

struct AgentsListView: View {
    @StateObject private var viewModel = AgentsListViewModel()
    
    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.agents.isEmpty {
                    LoadingView(message: "Loading agents...")
                } else if viewModel.agents.isEmpty {
                    EmptyStateView(
                        icon: "sparkles",
                        title: "No Agents",
                        message: "No agents available"
                    )
                } else {
                    List {
                        ForEach(viewModel.agents) { agent in
                            NavigationLink(destination: AgentDetailView(agent: agent)) {
                                AgentRow(agent: agent)
                            }
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("Agents")
            .refreshable {
                await viewModel.loadAgents()
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
        .task {
            await viewModel.loadAgents()
        }
    }
}

struct AgentRow: View {
    let agent: Agent
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color(hex: agent.color) ?? .accentColor)
                .frame(width: 44, height: 44)
                .overlay {
                    Text(agent.name.prefix(1))
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                }
            
            VStack(alignment: .leading, spacing: 2) {
                Text(agent.name)
                    .font(.headline)
                
                Text(agent.description)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text(agent.type.capitalized)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(agent.type == "premium" ? Color.orange.opacity(0.2) : Color.green.opacity(0.2))
                    .foregroundColor(agent.type == "premium" ? .orange : .green)
                    .cornerRadius(4)
                
                Text(agent.category.capitalized)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(.vertical, 4)
    }
}

@MainActor
final class AgentsListViewModel: ObservableObject {
    @Published var isLoading: Bool = false
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    @Published var agents: [Agent] = []
    
    private let patentRepository: PatentRepositoryProtocol
    
    init(patentRepository: PatentRepositoryProtocol? = nil) {
        let tokenStorage = TokenStorage()
        let settingsStorage = SettingsStorage()
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        self.patentRepository = patentRepository ?? PatentRepository(api: apiClient)
    }
    
    func loadAgents() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            agents = try await patentRepository.getAgents()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
