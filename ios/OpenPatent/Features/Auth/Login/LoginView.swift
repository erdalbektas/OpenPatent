import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var coordinator: AppCoordinator
    @StateObject private var viewModel = LoginViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: Constants.UI.largePadding) {
                Spacer()
                
                logoView
                
                titleSection
                
                formSection
                
                loginButton
                
                registerLink
                
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
            Text("Welcome to OpenPatent")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Sign in to access your patent workflow")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
    
    private var formSection: some View {
        VStack(spacing: Constants.UI.padding) {
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
                textContentType: .password
            )
            .textFieldStyle(OpenPatentTextFieldStyle())
        }
        .padding(.top, Constants.UI.largePadding)
    }
    
    private var loginButton: some View {
        Button {
            Task {
                await viewModel.login { email, password in
                    try await coordinator.login(email: email, password: password)
                }
            }
        } label: {
            if viewModel.isLoading {
                ProgressView()
                    .tint(.white)
            } else {
                Text("Sign In")
                    .fontWeight(.semibold)
            }
        }
        .buttonStyle(OpenPatentButtonStyle())
        .disabled(viewModel.isLoading || !viewModel.isFormValid)
    }
    
    private var registerLink: some View {
        HStack {
            Text("Don't have an account?")
                .foregroundStyle(.secondary)
            Button("Sign Up") {
                // Navigate to register
            }
            .fontWeight(.semibold)
        }
        .font(.subheadline)
    }
}

final class LoginViewModel: ObservableObject {
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var isLoading: Bool = false
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    
    var isFormValid: Bool {
        !email.isEmpty && !password.isEmpty && email.contains("@")
    }
    
    func login(action: (String, String) async throws -> Void) async {
        guard isFormValid else { return }
        
        isLoading = true
        defer { isLoading = false }
        
        do {
            try await action(email, password)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
