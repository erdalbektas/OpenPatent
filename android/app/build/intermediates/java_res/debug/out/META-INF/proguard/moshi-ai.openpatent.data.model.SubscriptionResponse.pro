-if class ai.openpatent.data.model.SubscriptionResponse
-keepnames class ai.openpatent.data.model.SubscriptionResponse
-if class ai.openpatent.data.model.SubscriptionResponse
-keep class ai.openpatent.data.model.SubscriptionResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.SubscriptionResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.SubscriptionResponse
-keepclassmembers class ai.openpatent.data.model.SubscriptionResponse {
    public synthetic <init>(ai.openpatent.data.model.Subscription,java.lang.String,boolean,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
