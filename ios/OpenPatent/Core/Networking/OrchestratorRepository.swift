import Foundation

protocol OrchestratorRepositoryProtocol {
    func createPlan(userRequest: String, technology: String) async throws -> OrchestrationPlan
    func executePlan(planId: String) async throws -> [OrchestrationPlan.OrchestrationTask]
    func getTemplates() async throws -> [String]
    func getThinking(sessionId: String) async throws -> [[String: String]]
}

final class OrchestratorRepository: OrchestratorRepositoryProtocol {
    private let api: ApiClientProtocol
    
    init(api: ApiClientProtocol) {
        self.api = api
    }
    
    func createPlan(userRequest: String, technology: String) async throws -> OrchestrationPlan {
        try await api.request(.createPlan, body: OrchestratorRequest(userRequest: userRequest, technology: technology, projectPath: nil))
    }
    
    func executePlan(planId: String) async throws -> [OrchestrationPlan.OrchestrationTask] {
        struct ExecuteResponse: Decodable {
            let tasks: [OrchestrationPlan.OrchestrationTask]
        }
        let response: ExecuteResponse = try await api.request(.executePlan, body: OrchestratorExecuteRequest(planId: planId))
        return response.tasks
    }
    
    func getTemplates() async throws -> [String] {
        struct TemplatesResponse: Decodable {
            let templates: [String]
        }
        let response: TemplatesResponse = try await api.request(.getTemplates, body: nil)
        return response.templates
    }
    
    func getThinking(sessionId: String) async throws -> [[String: String]] {
        struct ThinkingResponse: Decodable {
            let thinking: [[String: String]]
        }
        let response: ThinkingResponse = try await api.request(.getThinking(sessionId: sessionId), body: nil)
        return response.thinking
    }
}
