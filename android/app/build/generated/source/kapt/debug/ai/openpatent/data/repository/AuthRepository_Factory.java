package ai.openpatent.data.repository;

import ai.openpatent.data.local.SecureTokenStorage;
import ai.openpatent.data.remote.api.AuthApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class AuthRepository_Factory implements Factory<AuthRepository> {
  private final Provider<AuthApi> authApiProvider;

  private final Provider<SecureTokenStorage> tokenStorageProvider;

  public AuthRepository_Factory(Provider<AuthApi> authApiProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    this.authApiProvider = authApiProvider;
    this.tokenStorageProvider = tokenStorageProvider;
  }

  @Override
  public AuthRepository get() {
    return newInstance(authApiProvider.get(), tokenStorageProvider.get());
  }

  public static AuthRepository_Factory create(Provider<AuthApi> authApiProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    return new AuthRepository_Factory(authApiProvider, tokenStorageProvider);
  }

  public static AuthRepository newInstance(AuthApi authApi, SecureTokenStorage tokenStorage) {
    return new AuthRepository(authApi, tokenStorage);
  }
}
