-if class ai.openpatent.data.model.TemplateStep
-keepnames class ai.openpatent.data.model.TemplateStep
-if class ai.openpatent.data.model.TemplateStep
-keep class ai.openpatent.data.model.TemplateStepJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
