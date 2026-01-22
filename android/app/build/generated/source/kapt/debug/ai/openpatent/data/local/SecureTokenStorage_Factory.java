package ai.openpatent.data.local;

import android.content.Context;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class SecureTokenStorage_Factory implements Factory<SecureTokenStorage> {
  private final Provider<Context> contextProvider;

  public SecureTokenStorage_Factory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public SecureTokenStorage get() {
    return newInstance(contextProvider.get());
  }

  public static SecureTokenStorage_Factory create(Provider<Context> contextProvider) {
    return new SecureTokenStorage_Factory(contextProvider);
  }

  public static SecureTokenStorage newInstance(Context context) {
    return new SecureTokenStorage(context);
  }
}
