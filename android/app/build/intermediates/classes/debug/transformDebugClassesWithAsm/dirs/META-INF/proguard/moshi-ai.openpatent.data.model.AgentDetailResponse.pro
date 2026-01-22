-if class ai.openpatent.data.model.AgentDetailResponse
-keepnames class ai.openpatent.data.model.AgentDetailResponse
-if class ai.openpatent.data.model.AgentDetailResponse
-keep class ai.openpatent.data.model.AgentDetailResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.AgentDetailResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.AgentDetailResponse
-keepclassmembers class ai.openpatent.data.model.AgentDetailResponse {
    public synthetic <init>(ai.openpatent.data.model.Agent,java.util.List,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
