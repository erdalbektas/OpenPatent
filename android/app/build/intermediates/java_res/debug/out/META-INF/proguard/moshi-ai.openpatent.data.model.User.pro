-if class ai.openpatent.data.model.User
-keepnames class ai.openpatent.data.model.User
-if class ai.openpatent.data.model.User
-keep class ai.openpatent.data.model.UserJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.User
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.User
-keepclassmembers class ai.openpatent.data.model.User {
    public synthetic <init>(int,java.lang.String,java.lang.String,java.lang.String,int,int,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
