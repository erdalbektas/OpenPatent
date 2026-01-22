-if class ai.openpatent.data.model.AgentVersion
-keepnames class ai.openpatent.data.model.AgentVersion
-if class ai.openpatent.data.model.AgentVersion
-keep class ai.openpatent.data.model.AgentVersionJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.AgentVersion
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.AgentVersion
-keepclassmembers class ai.openpatent.data.model.AgentVersion {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
