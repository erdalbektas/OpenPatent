package ai.openpatent.di;

import ai.openpatent.data.local.SecureTokenStorage;
import ai.openpatent.data.remote.interceptor.AuthInterceptor;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

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
public final class AppModule_ProvideAuthInterceptorFactory implements Factory<AuthInterceptor> {
  private final Provider<SecureTokenStorage> tokenStorageProvider;

  public AppModule_ProvideAuthInterceptorFactory(
      Provider<SecureTokenStorage> tokenStorageProvider) {
    this.tokenStorageProvider = tokenStorageProvider;
  }

  @Override
  public AuthInterceptor get() {
    return provideAuthInterceptor(tokenStorageProvider.get());
  }

  public static AppModule_ProvideAuthInterceptorFactory create(
      Provider<SecureTokenStorage> tokenStorageProvider) {
    return new AppModule_ProvideAuthInterceptorFactory(tokenStorageProvider);
  }

  public static AuthInterceptor provideAuthInterceptor(SecureTokenStorage tokenStorage) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAuthInterceptor(tokenStorage));
  }
}
