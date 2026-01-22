# Add project specific ProGuard rules here.

# Keep Moshi adapters
-keep class ai.openpatent.data.model.** { *; }
-keepclassmembers class ai.openpatent.data.model.** { *; }

# Keep Retrofit interfaces
-keep,allowobfuscation interface ai.openpatent.data.remote.api.**

# Moshi
-keepclassmembers class * {
    @com.squareup.moshi.FromJson <methods>;
    @com.squareup.moshi.ToJson <methods>;
}

# Retrofit
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepattributes Signature
-keepattributes Exceptions

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
