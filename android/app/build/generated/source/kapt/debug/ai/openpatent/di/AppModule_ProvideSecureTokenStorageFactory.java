package ai.openpatent.di;

import ai.openpatent.data.local.SecureTokenStorage;
import android.content.Context;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata("dagger.hilt.android.qualifiers.ApplicationContext")
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
public final class AppModule_ProvideSecureTokenStorageFactory implements Factory<SecureTokenStorage> {
  private final Provider<Context> contextProvider;

  public AppModule_ProvideSecureTokenStorageFactory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public SecureTokenStorage get() {
    return provideSecureTokenStorage(contextProvider.get());
  }

  public static AppModule_ProvideSecureTokenStorageFactory create(
      Provider<Context> contextProvider) {
    return new AppModule_ProvideSecureTokenStorageFactory(contextProvider);
  }

  public static SecureTokenStorage provideSecureTokenStorage(Context context) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideSecureTokenStorage(context));
  }
}
