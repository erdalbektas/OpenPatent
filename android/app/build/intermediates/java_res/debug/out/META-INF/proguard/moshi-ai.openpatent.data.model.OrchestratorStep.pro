-if class ai.openpatent.data.model.OrchestratorStep
-keepnames class ai.openpatent.data.model.OrchestratorStep
-if class ai.openpatent.data.model.OrchestratorStep
-keep class ai.openpatent.data.model.OrchestratorStepJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.OrchestratorStep
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.OrchestratorStep
-keepclassmembers class ai.openpatent.data.model.OrchestratorStep {
    public synthetic <init>(java.lang.String,int,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.util.List,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
