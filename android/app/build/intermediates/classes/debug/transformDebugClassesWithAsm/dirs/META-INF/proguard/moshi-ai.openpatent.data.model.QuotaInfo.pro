-if class ai.openpatent.data.model.QuotaInfo
-keepnames class ai.openpatent.data.model.QuotaInfo
-if class ai.openpatent.data.model.QuotaInfo
-keep class ai.openpatent.data.model.QuotaInfoJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
