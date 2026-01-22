-if class ai.openpatent.data.model.OrchestratorPlan
-keepnames class ai.openpatent.data.model.OrchestratorPlan
-if class ai.openpatent.data.model.OrchestratorPlan
-keep class ai.openpatent.data.model.OrchestratorPlanJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.OrchestratorPlan
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.OrchestratorPlan
-keepclassmembers class ai.openpatent.data.model.OrchestratorPlan {
    public synthetic <init>(java.lang.String,java.lang.String,java.util.List,java.lang.String,java.lang.Double,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
