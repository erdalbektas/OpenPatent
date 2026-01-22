import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @StateObject private var viewModel = SettingsViewModel()
    @State private var showServerURLSheet = false
    @State private var showLogoutConfirmation = false
    
    var body: some View {
        NavigationStack {
            List {
                accountSection
                
                serverSection
                
                aboutSection
                
                logoutSection
            }
            .navigationTitle("Settings")
            .sheet(isPresented: $showServerURLSheet) {
                ServerURLSheet(viewModel: viewModel)
            }
            .alert("Sign Out", isPresented: $showLogoutConfirmation) {
                Button("Sign Out", role: .destructive) {
                    Task {
                        await coordinator.logout()
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Are you sure you want to sign out?")
            }
        }
    }
    
    private var accountSection: some View {
        Section("Account") {
            HStack {
                Image(systemName: "person.circle")
                    .font(.largeTitle)
                    .foregroundStyle(.secondary)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(viewModel.userEmail)
                        .font(.headline)
                    Text(viewModel.userName ?? "User")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(.vertical, 4)
        }
    }
    
    private var serverSection: some View {
        Section("Server") {
            HStack {
                Label("Server URL", systemImage: "server.rack")
                Spacer()
                Text(viewModel.serverURL)
                    .foregroundStyle(.secondary)
            }
            .onTapGesture {
                showServerURLSheet = true
            }
            
            HStack {
                Label("Version", systemImage: "info.circle")
                Spacer()
                Text(viewModel.appVersion)
                    .foregroundStyle(.secondary)
            }
        }
    }
    
    private var aboutSection: some View {
        Section("About") {
            Link(destination: URL(string: "https://openpatent.ai")!) {
                Label("Website", systemImage: "globe")
            }
            
            Link(destination: URL(string: "https://openpatent.ai/discord")!) {
                Label("Discord", systemImage: "bubble.left.and.bubble.right")
            }
            
            Link(destination: URL(string: "https://github.com/openpatent")!) {
                Label("GitHub", systemImage: "chevron.left.forwardslash.chevron.right")
            }
        }
    }
    
    private var logoutSection: some View {
        Section {
            Button(role: .destructive) {
                showLogoutConfirmation = true
            } label: {
                Label("Sign Out", systemImage: "rectangle.portrait.and.arrow.right")
            }
        }
    }
}

struct ServerURLSheet: View {
    @ObservedObject var viewModel: SettingsViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var tempURL: String = ""
    
    var body: some View {
        NavigationStack {
            Form {
                Section("Server URL") {
                    TextField("https://your-server.com", text: $tempURL)
                        .keyboardType(.URL)
                        .textContentType(.URL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                
                Section {
                    Text("Enter the URL of your OpenPatent server. Leave empty to use the default local server.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Server URL")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        viewModel.updateServerURL(tempURL)
                        dismiss()
                    }
                }
            }
            .onAppear {
                tempURL = viewModel.serverURL
            }
        }
    }
}

@MainActor
final class SettingsViewModel: ObservableObject {
    @Published var serverURL: String = ""
    @Published var userEmail: String = ""
    @Published var userName: String?
    @Published var appVersion: String = ""
    
    private let settingsStorage: SettingsStorage
    
    init(settingsStorage: SettingsStorage? = nil) {
        self.settingsStorage = settingsStorage ?? SettingsStorage()
        loadSettings()
        appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    }
    
    private func loadSettings() {
        serverURL = settingsStorage.serverURL
        userEmail = settingsStorage.userEmail ?? ""
        userName = settingsStorage.userName
    }
    
    func updateServerURL(_ url: String) {
        settingsStorage.serverURL = url
        serverURL = url
    }
}
