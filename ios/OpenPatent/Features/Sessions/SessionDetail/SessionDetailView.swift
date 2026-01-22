import SwiftUI

struct SessionDetailView: View {
    let sessionId: String
    @State private var session: PatentSession?
    @State private var isLoading = true
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        Group {
            if isLoading {
                LoadingView(message: "Loading session...")
            } else if let session = session {
                sessionContent(session)
            } else {
                ErrorView(message: "Session not found")
            }
        }
        .navigationTitle(session?.title ?? "Session")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadSession()
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }
    
    private func sessionContent(_ session: PatentSession) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Constants.UI.padding) {
                statusSection(session)
                
                if let inventionTitle = session.inventionTitle {
                    section(title: "Invention Title", content: inventionTitle)
                }
                
                if let inventionDescription = session.inventionDescription {
                    section(title: "Description", content: inventionDescription)
                }
                
                if let claims = session.claims, !claims.isEmpty {
                    claimsSection(claims)
                }
                
                if let specification = session.specification {
                    specificationSection(specification)
                }
            }
            .padding()
        }
    }
    
    private func statusSection(_ session: PatentSession) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Status")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(session.status.capitalized)
                    .font(.headline)
            }
            
            Spacer()
            
            if session.isPremium {
                Text("Premium")
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.2))
                    .foregroundColor(.orange)
                    .cornerRadius(4)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
    
    private func section(title: String, content: String) -> some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text(title)
                .font(.headline)
            Text(content)
                .foregroundStyle(.secondary)
        }
    }
    
    private func claimsSection(_ claims: [PatentSession.Claim]) -> some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Claims")
                .font(.headline)
            
            ForEach(claims) { claim in
                VStack(alignment: .leading, spacing: 4) {
                    Text("Claim \(claim.number)")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    Text(claim.text)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(Constants.UI.smallCornerRadius)
            }
        }
    }
    
    private func specificationSection(_ specification: PatentSession.Specification) -> some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Specification")
                .font(.headline)
            
            if let field = specification.field {
                section(title: "Field of Invention", content: field)
            }
            if let background = specification.background {
                section(title: "Background", content: background)
            }
            if let summary = specification.summary {
                section(title: "Summary", content: summary)
            }
            if let detailed = specification.detailedDescription {
                section(title: "Detailed Description", content: detailed)
            }
        }
    }
    
    private func loadSession() async {
        do {
            let tokenStorage = TokenStorage()
            let settingsStorage = SettingsStorage()
            let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
            let repository = PatentRepository(api: apiClient)
            session = try await repository.getSession(id: sessionId)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
        isLoading = false
    }
}
