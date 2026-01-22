import SwiftUI

struct SessionsListView: View {
    @StateObject private var viewModel = SessionsListViewModel()
    
    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.sessions.isEmpty {
                    LoadingView(message: "Loading sessions...")
                } else if viewModel.sessions.isEmpty {
                    EmptyStateView(
                        icon: "doc.text",
                        title: "No Sessions",
                        message: "Create your first patent session to get started",
                        actionTitle: "Create Session"
                    ) {
                        Task {
                            await viewModel.createSession()
                        }
                    }
                } else {
                    List {
                        ForEach(viewModel.sessions) { session in
                            NavigationLink(destination: SessionDetailView(sessionId: session.id)) {
                                SessionRow(session: session)
                            }
                        }
                        .onDelete { offsets in
                            Task { @MainActor in
                                await viewModel.deleteSessions(at: offsets)
                            }
                        }
                    }
                    .listStyle(.plain)
                    .refreshable {
                        await viewModel.refresh()
                    }
                }
            }
            .navigationTitle("Sessions")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Task {
                            await viewModel.createSession()
                        }
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
        .task {
            await viewModel.loadSessions()
        }
    }
}

struct SessionRow: View {
    let session: PatentSession
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(session.title)
                    .font(.headline)
                Spacer()
                Text(session.status.capitalized)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(statusColor.opacity(0.2))
                    .foregroundColor(statusColor)
                    .cornerRadius(4)
            }
            
            if let inventionTitle = session.inventionTitle {
                Text(inventionTitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
            
            Text(session.createdAt)
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding(.vertical, 4)
    }
    
    private var statusColor: Color {
        switch session.status {
        case "drafting": return .blue
        case "review": return .orange
        case "perfecting": return .purple
        case "filed": return .green
        case "examining": return .red
        default: return .gray
        }
    }
}

@MainActor
final class SessionsListViewModel: ObservableObject {
    @Published var isLoading: Bool = false
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    @Published var sessions: [PatentSession] = []
    
    private let patentRepository: PatentRepositoryProtocol
    
    init(patentRepository: PatentRepositoryProtocol? = nil) {
        let tokenStorage = TokenStorage()
        let settingsStorage = SettingsStorage()
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        self.patentRepository = patentRepository ?? PatentRepository(api: apiClient)
    }
    
    func loadSessions() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            sessions = try await patentRepository.getSessions()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
    
    func refresh() async {
        await loadSessions()
    }
    
    func createSession() async {
        do {
            let session = try await patentRepository.createSession(title: "New Patent Session")
            sessions.insert(session, at: 0)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
    
    func deleteSessions(at offsets: IndexSet) async {
        for index in offsets {
            let session = sessions[index]
            do {
                try await patentRepository.deleteSession(id: session.id)
            } catch {
                errorMessage = error.localizedDescription
                showError = true
            }
        }
        sessions.remove(atOffsets: offsets)
    }
}
