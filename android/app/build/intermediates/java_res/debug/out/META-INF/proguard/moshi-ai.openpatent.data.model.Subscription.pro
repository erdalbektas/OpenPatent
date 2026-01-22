-if class ai.openpatent.data.model.Subscription
-keepnames class ai.openpatent.data.model.Subscription
-if class ai.openpatent.data.model.Subscription
-keep class ai.openpatent.data.model.SubscriptionJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.Subscription
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.Subscription
-keepclassmembers class ai.openpatent.data.model.Subscription {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,boolean,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
