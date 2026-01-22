-if class ai.openpatent.data.model.PremiumAgentResponse
-keepnames class ai.openpatent.data.model.PremiumAgentResponse
-if class ai.openpatent.data.model.PremiumAgentResponse
-keep class ai.openpatent.data.model.PremiumAgentResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.PremiumAgentResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.PremiumAgentResponse
-keepclassmembers class ai.openpatent.data.model.PremiumAgentResponse {
    public synthetic <init>(boolean,ai.openpatent.data.model.AgentResult,java.lang.String,java.lang.Integer,java.lang.Double,java.lang.Integer,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
