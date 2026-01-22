-if class ai.openpatent.data.model.PriorArt
-keepnames class ai.openpatent.data.model.PriorArt
-if class ai.openpatent.data.model.PriorArt
-keep class ai.openpatent.data.model.PriorArtJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.PriorArt
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.PriorArt
-keepclassmembers class ai.openpatent.data.model.PriorArt {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,double,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
