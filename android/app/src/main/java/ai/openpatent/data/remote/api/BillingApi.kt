package ai.openpatent.data.remote.api

import ai.openpatent.data.model.*
import retrofit2.http.*

interface BillingApi {
    
    @GET("billing/subscription/")
    suspend fun getSubscriptionStatus(): SubscriptionResponse
    
    @GET("billing/pricing/")
    suspend fun getPricing(): PricingResponse
}
