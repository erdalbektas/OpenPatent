import Foundation

protocol BillingRepositoryProtocol {
    func getSubscription() async throws -> SubscriptionResponse
    func getPricing() async throws -> [PricingTier]
}

final class BillingRepository: BillingRepositoryProtocol {
    private let api: ApiClientProtocol
    
    init(api: ApiClientProtocol) {
        self.api = api
    }
    
    func getSubscription() async throws -> SubscriptionResponse {
        try await api.request(.getSubscription, body: nil)
    }
    
    func getPricing() async throws -> [PricingTier] {
        struct PricingResponse: Decodable {
            let tiers: [PricingTier]
        }
        let response: PricingResponse = try await api.request(.getPricing, body: nil)
        return response.tiers
    }
}
