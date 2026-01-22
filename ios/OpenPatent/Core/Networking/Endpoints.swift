import Foundation

enum Endpoint {
    case login
    case register
    case refreshToken
    case logout
    case getMe
    
    case getSessions
    case createSession
    case getSession(id: String)
    case updateSession(id: String)
    case deleteSession(id: String)
    
    case getAgents
    case getPremiumAgents
    case getAgent(id: String)
    case executePremiumAgent
    case getQuota
    
    case createPlan
    case executePlan
    case getTemplates
    case getThinking(sessionId: String)
    
    case getSubscription
    case getPricing
    
    var path: String {
        switch self {
        case .login:
            return "/api/auth/login/"
        case .register:
            return "/api/auth/register/"
        case .refreshToken:
            return "/api/auth/refresh/"
        case .logout:
            return "/api/auth/logout/"
        case .getMe:
            return "/api/auth/me/"
            
        case .getSessions:
            return "/api/patent/sessions/"
        case .createSession:
            return "/api/patent/sessions/"
        case .getSession(let id):
            return "/api/patent/sessions/\(id)/"
        case .updateSession(let id):
            return "/api/patent/sessions/\(id)/"
        case .deleteSession(let id):
            return "/api/patent/sessions/\(id)/"
            
        case .getAgents:
            return "/api/patent/agents/"
        case .getPremiumAgents:
            return "/api/patent/agents/premium/list/"
        case .getAgent(let id):
            return "/api/patent/agents/\(id)/"
        case .executePremiumAgent:
            return "/api/patent/agents/premium/"
        case .getQuota:
            return "/api/patent/quota/"
            
        case .createPlan:
            return "/api/patent/orchestrator/plan/"
        case .executePlan:
            return "/api/patent/orchestrator/execute/"
        case .getTemplates:
            return "/api/patent/orchestrator/templates/"
        case .getThinking(let sessionId):
            return "/api/patent/orchestrator/thinking/\(sessionId)/"
            
        case .getSubscription:
            return "/billing/subscription/"
        case .getPricing:
            return "/billing/pricing/"
        }
    }
    
    var method: String {
        switch self {
        case .login, .register, .createSession, .createPlan, .executePlan:
            return "POST"
        case .getSessions, .getSession, .getAgents, .getPremiumAgents, .getAgent,
             .getQuota, .getTemplates, .getThinking, .getMe, .getSubscription,
             .getPricing:
            return "GET"
        case .refreshToken:
            return "POST"
        case .updateSession:
            return "PATCH"
        case .deleteSession, .logout:
            return "POST"
        case .executePremiumAgent:
            return "POST"
        }
    }
    
    var requiresAuth: Bool {
        switch self {
        case .login, .register:
            return false
        default:
            return true
        }
    }
}
