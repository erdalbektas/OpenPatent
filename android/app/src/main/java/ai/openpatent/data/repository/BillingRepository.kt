package ai.openpatent.data.repository

import ai.openpatent.data.model.*
import ai.openpatent.data.remote.api.BillingApi
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class BillingRepository @Inject constructor(
    private val billingApi: BillingApi
) {
    suspend fun getSubscriptionStatus(): Result<SubscriptionResponse> {
        return try {
            val response = billingApi.getSubscriptionStatus()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getPricing(): Result<List<PricingPlan>> {
        return try {
            val response = billingApi.getPricing()
            Result.success(response.plans)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
