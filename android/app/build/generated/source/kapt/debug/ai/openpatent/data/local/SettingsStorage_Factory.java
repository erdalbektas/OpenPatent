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
public final class SettingsStorage_Factory implements Factory<SettingsStorage> {
  private final Provider<Context> contextProvider;

  public SettingsStorage_Factory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public SettingsStorage get() {
    return newInstance(contextProvider.get());
  }

  public static SettingsStorage_Factory create(Provider<Context> contextProvider) {
    return new SettingsStorage_Factory(contextProvider);
  }

  public static SettingsStorage newInstance(Context context) {
    return new SettingsStorage(context);
  }
}
