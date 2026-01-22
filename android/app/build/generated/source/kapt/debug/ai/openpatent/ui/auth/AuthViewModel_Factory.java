package ai.openpatent.ui.auth;

import ai.openpatent.data.local.SecureTokenStorage;
import ai.openpatent.data.local.SettingsStorage;
import ai.openpatent.data.repository.AuthRepository;
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
public final class AuthViewModel_Factory implements Factory<AuthViewModel> {
  private final Provider<AuthRepository> authRepositoryProvider;

  private final Provider<SettingsStorage> settingsStorageProvider;

  private final Provider<SecureTokenStorage> tokenStorageProvider;

  public AuthViewModel_Factory(Provider<AuthRepository> authRepositoryProvider,
      Provider<SettingsStorage> settingsStorageProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    this.authRepositoryProvider = authRepositoryProvider;
    this.settingsStorageProvider = settingsStorageProvider;
    this.tokenStorageProvider = tokenStorageProvider;
  }

  @Override
  public AuthViewModel get() {
    return newInstance(authRepositoryProvider.get(), settingsStorageProvider.get(), tokenStorageProvider.get());
  }

  public static AuthViewModel_Factory create(Provider<AuthRepository> authRepositoryProvider,
      Provider<SettingsStorage> settingsStorageProvider,
      Provider<SecureTokenStorage> tokenStorageProvider) {
    return new AuthViewModel_Factory(authRepositoryProvider, settingsStorageProvider, tokenStorageProvider);
  }

  public static AuthViewModel newInstance(AuthRepository authRepository,
      SettingsStorage settingsStorage, SecureTokenStorage tokenStorage) {
    return new AuthViewModel(authRepository, settingsStorage, tokenStorage);
  }
}
