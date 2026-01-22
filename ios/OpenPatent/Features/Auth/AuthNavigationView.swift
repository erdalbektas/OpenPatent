import SwiftUI

struct AuthNavigationView: View {
    @State private var showRegister = false
    
    var body: some View {
        NavigationStack {
            LoginView()
                .navigationDestination(isPresented: $showRegister) {
                    RegisterView()
                }
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Sign Up") {
                            showRegister = true
                        }
                    }
                }
        }
    }
}
