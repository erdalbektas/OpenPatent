import SwiftUI

struct OpenPatentTextField: View {
    @Binding var text: String
    var placeholder: String = ""
    var keyboardType: UIKeyboardType = .default
    var textContentType: UITextContentType?
    var autocapitalization: TextInputAutocapitalization = .sentences
    
    var body: some View {
        TextField(placeholder, text: $text)
            .keyboardType(keyboardType)
            .textContentType(textContentType)
            .textInputAutocapitalization(autocapitalization)
            .autocorrectionDisabled()
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(Constants.UI.cornerRadius)
    }
}

struct OpenPatentSecureField: View {
    @Binding var text: String
    var placeholder: String = ""
    var textContentType: UITextContentType?
    
    @State private var isVisible = false
    
    var body: some View {
        HStack {
            Group {
                if isVisible {
                    TextField(placeholder, text: $text)
                } else {
                    SecureField(placeholder, text: $text)
                }
            }
            .textContentType(textContentType)
            .autocorrectionDisabled()
            
            Button {
                isVisible.toggle()
            } label: {
                Image(systemName: isVisible ? "eye.slash" : "eye")
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
}

struct OpenPatentTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
    }
}

struct OpenPatentButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .frame(maxWidth: .infinity)
            .frame(height: Constants.UI.buttonHeight)
            .background(Color.accentColor)
            .foregroundColor(.white)
            .cornerRadius(Constants.UI.cornerRadius)
            .opacity(configuration.isPressed ? 0.7 : 1.0)
    }
}

struct QuotaStatusCard: View {
    let tier: String
    let used: Int
    let limit: Int
    
    var progress: Double {
        guard limit > 0 else { return 0 }
        return Double(used) / Double(limit)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            HStack {
                Text(tier.capitalized)
                    .font(.headline)
                Spacer()
                Text("\(used)/\(limit == 0 ? "∞" : "\(limit)")")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            
            ProgressView(value: progress)
                .tint(progress > 0.8 ? .red : .accentColor)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
}

struct SessionCard: View {
    let session: PatentSession
    
    var body: some View {
        VStack(alignment: .leading, spacing: Constants.UI.smallPadding) {
            HStack {
                Text(session.title)
                    .font(.headline)
                Spacer()
                statusBadge
            }
            
            if let inventionTitle = session.inventionTitle {
                Text(inventionTitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            
            Text(session.createdAt)
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(Constants.UI.cornerRadius)
    }
    
    private var statusBadge: some View {
        Text(session.status.capitalized)
            .font(.caption)
            .fontWeight(.medium)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(statusColor.opacity(0.2))
            .foregroundColor(statusColor)
            .cornerRadius(Constants.UI.smallCornerRadius)
    }
    
    private var statusColor: Color {
        switch session.status {
        case "drafting":
            return .blue
        case "review":
            return .orange
        case "perfecting":
            return .purple
        case "filed":
            return .green
        case "examining":
            return .red
        default:
            return .gray
        }
    }
}

struct AgentCard: View {
    let agent: Agent
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: Constants.UI.smallPadding) {
                Circle()
                    .fill(Color(hex: agent.color) ?? .accentColor)
                    .frame(width: 40, height: 40)
                    .overlay {
                        Text(agent.name.prefix(1))
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(agent.name)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(agent.description)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                
                Spacer()
                
                Text(agent.type.capitalized)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(agent.type == "premium" ? Color.orange.opacity(0.2) : Color.green.opacity(0.2))
                    .foregroundColor(agent.type == "premium" ? .orange : .green)
                    .cornerRadius(Constants.UI.smallCornerRadius)
                
                Image(systemName: "chevron.right")
                    .foregroundStyle(.tertiary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(Constants.UI.cornerRadius)
        }
        .buttonStyle(.plain)
    }
}

struct LoadingView: View {
    var message: String = "Loading..."
    
    var body: some View {
        VStack(spacing: Constants.UI.padding) {
            ProgressView()
            Text(message)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ErrorView: View {
    let message: String
    var retryAction: (() -> Void)?
    
    var body: some View {
        VStack(spacing: Constants.UI.padding) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundStyle(.orange)
            
            Text(message)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
            
            if let retry = retryAction {
                Button("Retry", action: retry)
                    .buttonStyle(OpenPatentButtonStyle())
            }
        }
        .padding()
    }
}

struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    var actionTitle: String?
    var action: (() -> Void)?
    
    var body: some View {
        VStack(spacing: Constants.UI.padding) {
            Image(systemName: icon)
                .font(.system(size: 50))
                .foregroundStyle(.secondary)
            
            Text(title)
                .font(.headline)
            
            Text(message)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
            
            if let actionTitle = actionTitle, let action = action {
                Button(actionTitle, action: action)
                    .buttonStyle(OpenPatentButtonStyle())
            }
        }
        .padding()
    }
}

extension Color {
    init?(hex: String) {
        var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        hexSanitized = hexSanitized.replacingOccurrences(of: "#", with: "")
        
        guard hexSanitized.count == 6 else { return nil }
        
        var rgb: UInt64 = 0
        Scanner(string: hexSanitized).scanHexInt64(&rgb)
        
        self.init(
            red: Double((rgb & 0xFF0000) >> 16) / 255.0,
            green: Double((rgb & 0x00FF00) >> 8) / 255.0,
            blue: Double(rgb & 0x0000FF) / 255.0
        )
    }
}
