-if class ai.openpatent.data.model.OrchestratorTemplate
-keepnames class ai.openpatent.data.model.OrchestratorTemplate
-if class ai.openpatent.data.model.OrchestratorTemplate
-keep class ai.openpatent.data.model.OrchestratorTemplateJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.OrchestratorTemplate
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.OrchestratorTemplate
-keepclassmembers class ai.openpatent.data.model.OrchestratorTemplate {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.util.List,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
