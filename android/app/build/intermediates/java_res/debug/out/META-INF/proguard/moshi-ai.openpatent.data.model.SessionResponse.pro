-if class ai.openpatent.data.model.SessionResponse
-keepnames class ai.openpatent.data.model.SessionResponse
-if class ai.openpatent.data.model.SessionResponse
-keep class ai.openpatent.data.model.SessionResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.SessionResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.SessionResponse
-keepclassmembers class ai.openpatent.data.model.SessionResponse {
    public synthetic <init>(ai.openpatent.data.model.PatentSession,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
