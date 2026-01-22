-if class ai.openpatent.data.model.SessionsListResponse
-keepnames class ai.openpatent.data.model.SessionsListResponse
-if class ai.openpatent.data.model.SessionsListResponse
-keep class ai.openpatent.data.model.SessionsListResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.SessionsListResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.SessionsListResponse
-keepclassmembers class ai.openpatent.data.model.SessionsListResponse {
    public synthetic <init>(java.util.List,java.lang.Integer,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
