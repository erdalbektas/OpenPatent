package ai.openpatent.data.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// ============ Subscription Status ============

@JsonClass(generateAdapter = true)
data class SubscriptionResponse(
    val subscription: Subscription? = null,
    val tier: String = "free",
    val active: Boolean = false
)

@JsonClass(generateAdapter = true)
data class Subscription(
    val id: String? = null,
    val plan: String,
    val status: String, // "active", "canceled", "past_due", "trialing"
    @Json(name = "current_period_start") val currentPeriodStart: String? = null,
    @Json(name = "current_period_end") val currentPeriodEnd: String? = null,
    @Json(name = "cancel_at_period_end") val cancelAtPeriodEnd: Boolean = false,
    @Json(name = "stripe_subscription_id") val stripeSubscriptionId: String? = null
)

// ============ Pricing ============

@JsonClass(generateAdapter = true)
data class PricingResponse(
    val plans: List<PricingPlan>
)

@JsonClass(generateAdapter = true)
data class PricingPlan(
    val id: String,
    val name: String,
    val price: Int, // In cents
    @Json(name = "price_id") val priceId: String? = null,
    @Json(name = "requests_per_hour") val requestsPerHour: Int,
    @Json(name = "tokens_per_hour") val tokensPerHour: Int,
    val features: List<String> = emptyList(),
    @Json(name = "agent_quotas") val agentQuotas: Map<String, Int>? = null,
    val popular: Boolean = false
)

// ============ Subscription Tier Enum ============

enum class SubscriptionTier(val displayName: String) {
    FREE("Free"),
    PRO("Pro"),
    ENTERPRISE("Enterprise");

    companion object {
        fun fromString(value: String): SubscriptionTier {
            return when (value.lowercase()) {
                "pro" -> PRO
                "enterprise" -> ENTERPRISE
                else -> FREE
            }
        }
    }
}
