import SwiftUI

struct RegisterView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @StateObject private var viewModel = RegisterViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: Constants.UI.largePadding) {
                Spacer()
                
                logoView
                
                titleSection
                
                formSection
                
                registerButton
                
                loginLink
                
                Spacer()
            }
            .padding(Constants.UI.padding)
        }
        .alert("Error", isPresented: $viewModel.showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage)
        }
    }
    
    private var logoView: some View {
        Image(systemName: "doc.text.magnifyingglass")
            .font(.system(size: 60))
            .foregroundColor(.accentColor)
    }
    
    private var titleSection: some View {
        VStack(spacing: Constants.UI.smallPadding) {
            Text("Create Account")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Start your patent workflow today")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
    
    private var formSection: some View {
        VStack(spacing: Constants.UI.padding) {
            OpenPatentTextField(
                text: $viewModel.username,
                placeholder: "Username (optional)",
                textContentType: .username,
                autocapitalization: .never
            )
            .textFieldStyle(OpenPatentTextFieldStyle())
            
            OpenPatentTextField(
                text: $viewModel.email,
                placeholder: "Email",
                keyboardType: .emailAddress,
                textContentType: .emailAddress,
                autocapitalization: .never
            )
            .textFieldStyle(OpenPatentTextFieldStyle())
            
            OpenPatentSecureField(
                text: $viewModel.password,
                placeholder: "Password",
                textContentType: .newPassword
            )
            .textFieldStyle(OpenPatentTextFieldStyle())
        }
        .padding(.top, Constants.UI.largePadding)
    }
    
    private var registerButton: some View {
        Button {
            Task {
                await viewModel.register { email, password, username in
                    try await coordinator.register(email: email, password: password, username: username)
                }
            }
        } label: {
            if viewModel.isLoading {
                ProgressView()
                    .tint(.white)
            } else {
                Text("Create Account")
                    .fontWeight(.semibold)
            }
        }
        .buttonStyle(OpenPatentButtonStyle())
        .disabled(viewModel.isLoading || !viewModel.isFormValid)
    }
    
    private var loginLink: some View {
        HStack {
            Text("Already have an account?")
                .foregroundStyle(.secondary)
            Button("Sign In") {
                // Navigate back to login
            }
            .fontWeight(.semibold)
        }
        .font(.subheadline)
    }
}

final class RegisterViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var isLoading: Bool = false
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    
    var isFormValid: Bool {
        !email.isEmpty && !password.isEmpty && email.contains("@") && password.count >= 8
    }
    
    func register(action: (String, String, String?) async throws -> Void) async {
        guard isFormValid else { return }
        
        isLoading = true
        defer { isLoading = false }
        
        do {
            try await action(email, password, username.isEmpty ? nil : username)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
