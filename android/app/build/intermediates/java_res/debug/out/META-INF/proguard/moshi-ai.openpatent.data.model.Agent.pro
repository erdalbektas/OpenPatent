-if class ai.openpatent.data.model.Agent
-keepnames class ai.openpatent.data.model.Agent
-if class ai.openpatent.data.model.Agent
-keep class ai.openpatent.data.model.AgentJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.Agent
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.Agent
-keepclassmembers class ai.openpatent.data.model.Agent {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,boolean,java.lang.Integer,java.lang.Integer,java.util.List,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
