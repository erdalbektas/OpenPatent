import Foundation

protocol PatentRepositoryProtocol {
    func getSessions() async throws -> [PatentSession]
    func createSession(title: String) async throws -> PatentSession
    func getSession(id: String) async throws -> PatentSession
    func updateSession(id: String, title: String?) async throws -> PatentSession
    func deleteSession(id: String) async throws
    func getQuota() async throws -> QuotaResponse
    func getAgents() async throws -> [Agent]
    func getPremiumAgents() async throws -> [Agent]
    func executePremiumAgent(agentType: String, task: String, context: [String: String]) async throws -> PremiumAgentResponse
}

final class PatentRepository: PatentRepositoryProtocol {
    private let api: ApiClientProtocol
    
    init(api: ApiClientProtocol) {
        self.api = api
    }
    
    func getSessions() async throws -> [PatentSession] {
        try await api.request(.getSessions, body: nil)
    }
    
    func createSession(title: String) async throws -> PatentSession {
        struct CreateRequest: Encodable {
            let title: String
        }
        return try await api.request(.createSession, body: CreateRequest(title: title))
    }
    
    func getSession(id: String) async throws -> PatentSession {
        try await api.request(.getSession(id: id), body: nil)
    }
    
    func updateSession(id: String, title: String?) async throws -> PatentSession {
        struct UpdateRequest: Encodable {
            let title: String?
        }
        return try await api.request(.updateSession(id: id), body: UpdateRequest(title: title))
    }
    
    func deleteSession(id: String) async throws {
        let _: EmptyResponse = try await api.request(.deleteSession(id: id), body: nil)
    }
    
    private struct EmptyResponse: Decodable {}
    
    func getQuota() async throws -> QuotaResponse {
        try await api.request(.getQuota, body: nil)
    }
    
    func getAgents() async throws -> [Agent] {
        struct AgentsResponse: Decodable {
            let agents: [Agent]
            let count: Int
        }
        let response: AgentsResponse = try await api.request(.getAgents, body: nil)
        return response.agents
    }
    
    func getPremiumAgents() async throws -> [Agent] {
        struct PremiumAgentsResponse: Decodable {
            let agents: [Agent]
        }
        let response: PremiumAgentsResponse = try await api.request(.getPremiumAgents, body: nil)
        return response.agents
    }
    
    func executePremiumAgent(agentType: String, task: String, context: [String: String]) async throws -> PremiumAgentResponse {
        struct ExecuteRequest: Encodable {
            let agent_type: String
            let task: String
            let context: [String: String]
        }
        return try await api.request(.executePremiumAgent, body: ExecuteRequest(agent_type: agentType, task: task, context: context))
    }
}
