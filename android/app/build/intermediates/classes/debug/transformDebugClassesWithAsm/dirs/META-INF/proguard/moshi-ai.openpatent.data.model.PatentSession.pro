-if class ai.openpatent.data.model.PatentSession
-keepnames class ai.openpatent.data.model.PatentSession
-if class ai.openpatent.data.model.PatentSession
-keep class ai.openpatent.data.model.PatentSessionJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.PatentSession
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.PatentSession
-keepclassmembers class ai.openpatent.data.model.PatentSession {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.util.List,java.util.Map,java.util.List,java.util.List,boolean,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
