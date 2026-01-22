package ai.openpatent.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ai.openpatent.ui.theme.*

/**
 * Progress bar showing quota usage with color coding.
 */
@Composable
fun QuotaBar(
    label: String,
    used: Int,
    limit: Int,
    modifier: Modifier = Modifier
) {
    val progress = if (limit > 0) used.toFloat() / limit.toFloat() else 0f
    val progressColor = when {
        progress >= 0.9f -> Error
        progress >= 0.7f -> Warning
        else -> Success
    }
    
    Column(
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            Text(
                text = "$used / $limit",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        LinearProgressIndicator(
            progress = progress.coerceIn(0f, 1f),
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            color = progressColor,
            trackColor = MaterialTheme.colorScheme.surfaceVariant,
        )
    }
}

/**
 * Card showing quota status for multiple agent types.
 */
@Composable
fun QuotaStatusCard(
    tier: String,
    quotas: Map<String, Pair<Int, Int>>, // agent_type -> (used, limit)
    resetDate: String?,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Quota Status",
                    style = MaterialTheme.typography.titleMedium
                )
                TierBadge(tier = tier)
            }
            
            if (resetDate != null) {
                Text(
                    text = "Resets: $resetDate",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            quotas.forEach { (agentType, quota) ->
                val (used, limit) = quota
                QuotaBar(
                    label = formatAgentType(agentType),
                    used = used,
                    limit = limit,
                    modifier = Modifier.padding(vertical = 4.dp)
                )
            }
        }
    }
}

@Composable
fun TierBadge(tier: String) {
    val (color, text) = when (tier.lowercase()) {
        "pro" -> TierPro to "Pro"
        "enterprise" -> TierEnterprise to "Enterprise"
        else -> TierFree to "Free"
    }
    
    Surface(
        color = color,
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onPrimary,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

private fun formatAgentType(agentType: String): String {
    return agentType
        .replace("_", " ")
        .split(" ")
        .joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } }
}
