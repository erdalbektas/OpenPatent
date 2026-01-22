-if class ai.openpatent.data.model.PricingPlan
-keepnames class ai.openpatent.data.model.PricingPlan
-if class ai.openpatent.data.model.PricingPlan
-keep class ai.openpatent.data.model.PricingPlanJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class ai.openpatent.data.model.PricingPlan
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class ai.openpatent.data.model.PricingPlan
-keepclassmembers class ai.openpatent.data.model.PricingPlan {
    public synthetic <init>(java.lang.String,java.lang.String,int,java.lang.String,int,int,java.util.List,java.util.Map,boolean,int,kotlin.jvm.internal.DefaultConstructorMarker);
}
