package ai.openpatent.di;

import ai.openpatent.data.local.SecureTokenStorage;
import ai.openpatent.data.remote.api.AuthApi;
import ai.openpatent.data.repository.AuthRepository;
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
public final class AppModule_ProvideAuthRepositoryFactory implements Factory<AuthRepository> {
  private final Provider<AuthApi> authApiProvider;

  private final Provider<SecureTokenStorage> tokenStorageProvider;

  public AppModule_ProvideAuthRepositoryFactory(Provider<AuthApi> authApiProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    this.authApiProvider = authApiProvider;
    this.tokenStorageProvider = tokenStorageProvider;
  }

  @Override
  public AuthRepository get() {
    return provideAuthRepository(authApiProvider.get(), tokenStorageProvider.get());
  }

  public static AppModule_ProvideAuthRepositoryFactory create(Provider<AuthApi> authApiProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    return new AppModule_ProvideAuthRepositoryFactory(authApiProvider, tokenStorageProvider);
  }

  public static AuthRepository provideAuthRepository(AuthApi authApi,
      SecureTokenStorage tokenStorage) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAuthRepository(authApi, tokenStorage));
  }
}
