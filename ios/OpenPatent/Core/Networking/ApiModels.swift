import Foundation

// MARK: - Auth Models

struct AuthResponse: Codable {
    let access: String
    let refresh: String
    let user: UserResponse
}

struct UserResponse: Codable {
    let id: String
    let email: String
    let username: String?
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let email: String
    let password: String
    let username: String?
}

struct TokenResponse: Codable {
    let access: String
    let refresh: String
}

// MARK: - Patent Models

struct PatentSession: Codable, Identifiable {
    let id: String
    var title: String
    let user: String
    var inventionTitle: String?
    var inventionDescription: String?
    var claims: [Claim]?
    var specification: Specification?
    var status: String
    let isPremium: Bool
    let createdAt: String
    var updatedAt: String
    
    struct Claim: Codable, Identifiable {
        let id: String
        var number: Int
        var text: String
        var type: String
        var dependsOn: Int?
    }
    
    struct Specification: Codable {
        var field: String?
        var background: String?
        var summary: String?
        var detailedDescription: String?
    }
}

struct QuotaResponse: Codable {
    let tier: String
    let quotas: [String: QuotaInfo]
    
    struct QuotaInfo: Codable {
        let used: Int
        let limit: Int
        let remaining: Int
    }
}

// MARK: - Agent Models

struct Agent: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
    let type: String
    let category: String
    let version: String
    let allowedModes: [String]
    let color: String
    let icon: String
    let tags: [String]
    let systemPrompt: String?
}

struct PremiumAgentResponse: Codable {
    let success: Bool
    let result: [String: AnyCodableValue]?
    let error: String?
    let tokensUsed: Int?
    let cost: Double?
}

struct AnyCodableValue: Codable {
    let value: Any
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodableValue].self) {
            value = array.map { $0.value }
        } else if let dict = try? container.decode([String: AnyCodableValue].self) {
            value = dict.mapValues { $0.value }
        } else {
            value = NSNull()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch value {
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodableValue(value: $0) })
        case let dict as [String: Any]:
            try container.encode(dict.mapValues { AnyCodableValue(value: $0) })
        default:
            try container.encodeNil()
        }
    }
    
    init(value: Any) {
        self.value = value
    }
}

// MARK: - Orchestrator Models

struct OrchestrationPlan: Codable, Identifiable {
    let id: String
    let userRequest: String
    let technology: String
    let tasks: [OrchestrationTask]
    let createdAt: String
    
    struct OrchestrationTask: Codable, Identifiable {
        let id: String
        let task: String
        let agent: String
        let inputData: [String: String]
        let dependsOn: [String]
        var status: String
        var result: String?
    }
}

struct OrchestratorRequest: Codable {
    let userRequest: String
    let technology: String
    let projectPath: String?
}

struct OrchestratorExecuteRequest: Codable {
    let planId: String
}

// MARK: - Billing Models

struct SubscriptionResponse: Codable {
    let tier: String
    let status: String
    let currentPeriodEnd: String?
}

struct PricingTier: Codable, Identifiable {
    let id: String
    let name: String
    let price: String
    let features: [String]
}
