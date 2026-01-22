-if class ai.openpatent.data.model.ThinkingEntry
-keepnames class ai.openpatent.data.model.ThinkingEntry
-if class ai.openpatent.data.model.ThinkingEntry
-keep class ai.openpatent.data.model.ThinkingEntryJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.ThinkingEntry
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.ThinkingEntry
-keepclassmembers class ai.openpatent.data.model.ThinkingEntry {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
