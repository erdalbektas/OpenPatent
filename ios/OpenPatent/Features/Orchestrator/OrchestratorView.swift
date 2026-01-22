import SwiftUI

struct OrchestratorView: View {
    @State private var userRequest = ""
    @State private var selectedTechnology = "software"
    @State private var isCreatingPlan = false
    @State private var plan: OrchestrationPlan?
    @State private var isExecuting = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    let technologies = ["software", "ai", "biotech", "mechanics"]
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: Constants.UI.padding) {
                    descriptionSection
                    
                    requestSection
                    
                    technologySection
                    
                    createPlanButton
                    
                    if let plan = plan {
                        planSection(plan)
                    }
                }
                .padding()
            }
            .navigationTitle("Orchestrator")
            .alert("Error", isPresented: $showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(errorMessage)
            }
        }
    }
    
    private var descriptionSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("AI-Powered Patent Planning")
                .font(.headline)
            Text("Describe your invention and let the orchestrator create a comprehensive patent workflow plan.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
    
    private var requestSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("What would you like to patent?")
                .font(.headline)
            
            TextEditor(text: $userRequest)
                .frame(minHeight: 150)
                .padding(8)
                .background(Color(.systemGray6))
                .cornerRadius(Constants.UI.cornerRadius)
        }
    }
    
    private var technologySection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Technology Type")
                .font(.headline)
            
            Picker("Technology", selection: $selectedTechnology) {
                ForEach(technologies, id: \.self) { tech in
                    Text(tech.capitalized).tag(tech)
                }
            }
            .pickerStyle(.segmented)
        }
    }
    
    private var createPlanButton: some View {
        Button {
            Task {
                await createPlan()
            }
        } label: {
            if isCreatingPlan {
                ProgressView()
                    .tint(.white)
            } else {
                Text("Create Plan")
            }
        }
        .buttonStyle(OpenPatentButtonStyle())
        .disabled(userRequest.isEmpty || isCreatingPlan)
    }
    
    private func planSection(_ plan: OrchestrationPlan) -> some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Generated Plan")
                .font(.headline)
            
            ForEach(plan.tasks) { task in
                TaskCard(task: task)
            }
            
            Button {
                Task {
                    await executePlan()
                }
            } label: {
                if isExecuting {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Execute Plan")
                }
            }
            .buttonStyle(OpenPatentButtonStyle())
            .disabled(isExecuting)
        }
    }
    
    private func createPlan() async {
        isCreatingPlan = true
        
        do {
            let tokenStorage = TokenStorage()
            let settingsStorage = SettingsStorage()
            let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
            let repository = OrchestratorRepository(api: apiClient)
            
            plan = try await repository.createPlan(userRequest: userRequest, technology: selectedTechnology)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
        
        isCreatingPlan = false
    }
    
    private func executePlan() async {
        guard let plan = plan else { return }
        
        isExecuting = true
        
        do {
            let tokenStorage = TokenStorage()
            let settingsStorage = SettingsStorage()
            let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
            let repository = OrchestratorRepository(api: apiClient)
            
            _ = try await repository.executePlan(planId: plan.id)
            
            // Refresh plan to get updated task status
            self.plan = try await repository.createPlan(userRequest: userRequest, technology: selectedTechnology)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
        
        isExecuting = false
    }
}

struct TaskCard: View {
    let task: OrchestrationPlan.OrchestrationTask
    
    var body: some View {
        HStack {
            Circle()
                .fill(statusColor)
                .frame(width: 24, height: 24)
                .overlay {
                    if task.status == "completed" {
                        Image(systemName: "checkmark")
                            .font(.caption2)
                            .foregroundColor(.white)
                    }
                }
            
            VStack(alignment: .leading, spacing: 2) {
                Text(task.task)
                    .font(.subheadline)
                    .fontWeight(.medium)
                HStack {
                    Text(task.agent)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(task.status.capitalized)
                        .font(.caption)
                        .foregroundStyle(statusColor)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
    
    private var statusColor: Color {
        switch task.status {
        case "completed": return .green
        case "failed": return .red
        case "running": return .blue
        default: return .gray
        }
    }
}
