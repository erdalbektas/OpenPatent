package ai.openpatent.data.remote.interceptor;

import ai.openpatent.data.local.SecureTokenStorage;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
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
public final class AuthInterceptor_Factory implements Factory<AuthInterceptor> {
  private final Provider<SecureTokenStorage> tokenStorageProvider;

  public AuthInterceptor_Factory(Provider<SecureTokenStorage> tokenStorageProvider) {
    this.tokenStorageProvider = tokenStorageProvider;
  }

  @Override
  public AuthInterceptor get() {
    return newInstance(tokenStorageProvider.get());
  }

  public static AuthInterceptor_Factory create(Provider<SecureTokenStorage> tokenStorageProvider) {
    return new AuthInterceptor_Factory(tokenStorageProvider);
  }

  public static AuthInterceptor newInstance(SecureTokenStorage tokenStorage) {
    return new AuthInterceptor(tokenStorage);
  }
}
