package ai.openpatent.di;

import ai.openpatent.data.local.SettingsStorage;
import com.squareup.moshi.Moshi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import okhttp3.OkHttpClient;
import retrofit2.Retrofit;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class AppModule_ProvideRetrofitFactory implements Factory<Retrofit> {
  private final Provider<OkHttpClient> okHttpClientProvider;

  private final Provider<Moshi> moshiProvider;

  private final Provider<SettingsStorage> settingsStorageProvider;

  public AppModule_ProvideRetrofitFactory(Provider<OkHttpClient> okHttpClientProvider,
      Provider<Moshi> moshiProvider, Provider<SettingsStorage> settingsStorageProvider) {
    this.okHttpClientProvider = okHttpClientProvider;
    this.moshiProvider = moshiProvider;
    this.settingsStorageProvider = settingsStorageProvider;
  }

  @Override
  public Retrofit get() {
    return provideRetrofit(okHttpClientProvider.get(), moshiProvider.get(), settingsStorageProvider.get());
  }

  public static AppModule_ProvideRetrofitFactory create(Provider<OkHttpClient> okHttpClientProvider,
      Provider<Moshi> moshiProvider, Provider<SettingsStorage> settingsStorageProvider) {
    return new AppModule_ProvideRetrofitFactory(okHttpClientProvider, moshiProvider, settingsStorageProvider);
  }

  public static Retrofit provideRetrofit(OkHttpClient okHttpClient, Moshi moshi,
      SettingsStorage settingsStorage) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideRetrofit(okHttpClient, moshi, settingsStorage));
  }
}
