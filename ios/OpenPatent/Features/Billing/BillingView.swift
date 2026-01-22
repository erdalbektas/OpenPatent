import SwiftUI

struct BillingView: View {
    @StateObject private var viewModel = BillingViewModel()
    
    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    LoadingView(message: "Loading subscription...")
                } else {
                    ScrollView {
                        VStack(spacing: Constants.UI.padding) {
                            currentPlanSection
                            
                            pricingSection
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Billing")
            .task {
                await viewModel.loadData()
            }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage)
            }
        }
    }
    
    private var currentPlanSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Current Plan")
                .font(.headline)
            
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(viewModel.subscription.tier.capitalized)
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text(viewModel.subscription.status.capitalized)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                
                Spacer()
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(Constants.UI.cornerRadius)
        }
    }
    
    private var pricingSection: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            Text("Available Plans")
                .font(.headline)
            
            ForEach(viewModel.pricingTiers) { tier in
                PricingCard(
                    tier: tier,
                    isCurrent: tier.id == viewModel.subscription.tier
                )
            }
        }
    }
}

struct PricingCard: View {
    let tier: PricingTier
    let isCurrent: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(tier.name)
                        .font(.headline)
                    Text(tier.price)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.accentColor)
                }
                
                Spacer()
                
                if isCurrent {
                    Text("Current")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.2))
                        .foregroundColor(.green)
                        .cornerRadius(4)
                }
            }
            
            ForEach(tier.features, id: \.self) { feature in
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                    Text(feature)
                        .font(.caption)
                }
            }
            
            if !isCurrent {
                Button("Upgrade") {
                    // Open Stripe checkout
                }
                .buttonStyle(OpenPatentButtonStyle())
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
}

@MainActor
final class BillingViewModel: ObservableObject {
    @Published var isLoading = true
    @Published var showError = false
    @Published var errorMessage = ""
    @Published var subscription = SubscriptionResponse(tier: "free", status: "active", currentPeriodEnd: nil)
    @Published var pricingTiers: [PricingTier] = []
    
    private let billingRepository: BillingRepositoryProtocol
    
    init(billingRepository: BillingRepositoryProtocol? = nil) {
        let tokenStorage = TokenStorage()
        let settingsStorage = SettingsStorage()
        let apiClient = ApiClient(tokenStorage: tokenStorage, settingsStorage: settingsStorage)
        self.billingRepository = billingRepository ?? BillingRepository(api: apiClient)
    }
    
    func loadData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            async let subscriptionResult = billingRepository.getSubscription()
            async let pricingResult = billingRepository.getPricing()
            
            let (sub, pricing) = try await (subscriptionResult, pricingResult)
            subscription = sub
            pricingTiers = pricing
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
