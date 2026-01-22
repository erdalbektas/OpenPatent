import SwiftUI

struct AgentDetailView: View {
    let agent: Agent
    @State private var taskInput = ""
    @State private var isExecuting = false
    @State private var result: PremiumAgentResponse?
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Constants.UI.padding) {
                agentHeader
                
                if agent.type == "premium" {
                    executionSection
                }
                
                if let result = result {
                    resultSection(result)
                }
            }
            .padding()
        }
        .navigationTitle(agent.name)
        .navigationBarTitleDisplayMode(.inline)
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }
    
    private var agentHeader: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            HStack {
                Circle()
                    .fill(Color(hex: agent.color) ?? .accentColor)
                    .frame(width: 60, height: 60)
                    .overlay {
                        Text(agent.name.prefix(1))
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(agent.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    HStack {
                        Text(agent.type.capitalized)
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(agent.type == "premium" ? Color.orange.opacity(0.2) : Color.green.opacity(0.2))
                            .foregroundColor(agent.type == "premium" ? .orange : .green)
                            .cornerRadius(4)
                        
                        Text(agent.category.capitalized)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            
            Text(agent.description)
                .font(.body)
                .foregroundStyle(.secondary)
            
            if !agent.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: Constants.UI.smallPadding) {
                        ForEach(agent.tags, id: \.self) { tag in
                            Text(tag)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color(.systemGray5))
                                .cornerRadius(4)
                        }
                    }
                }
            }
        }
    }
    
    private var executionSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Execute Agent")
                .font(.headline)
            
            TextEditor(text: $taskInput)
                .frame(minHeight: 150)
                .padding(8)
                .background(Color(.systemGray6))
                .cornerRadius(Constants.UI.cornerRadius)
            
            Button {
                Task {
                    await executeAgent()
                }
            } label: {
                if isExecuting {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Execute")
                }
            }
            .buttonStyle(OpenPatentButtonStyle())
            .disabled(taskInput.isEmpty || isExecuting)
        }
    }
    
    private func resultSection(_ result: PremiumAgentResponse) -> some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Result")
                .font(.headline)
            
            if result.success {
                Text("Execution completed successfully")
                    .foregroundColor(.green)
                
                if let tokenCount = result.tokensUsed {
                    Text("Tokens used: \(tokenCount)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            } else {
                Text("Execution failed: \(result.error ?? "Unknown error")")
                    .foregroundColor(.red)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
    
    private func executeAgent() async {
        isExecuting = true
        
        do {
            let tokenStorage = TokenStorage()
            let settingsStorage = SettingsStorage()
            let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
            let repository = PatentRepository(api: apiClient)
            
            let response = try await repository.executePremiumAgent(
                agentType: agent.id,
                task: taskInput,
                context: [:]
            )
            
            self.result = response
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
        
        isExecuting = false
    }
}
