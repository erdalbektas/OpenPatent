package ai.openpatent.di;

import ai.openpatent.data.local.SettingsStorage;
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
public final class AppModule_ProvideSettingsStorageFactory implements Factory<SettingsStorage> {
  private final Provider<Context> contextProvider;

  public AppModule_ProvideSettingsStorageFactory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public SettingsStorage get() {
    return provideSettingsStorage(contextProvider.get());
  }

  public static AppModule_ProvideSettingsStorageFactory create(Provider<Context> contextProvider) {
    return new AppModule_ProvideSettingsStorageFactory(contextProvider);
  }

  public static SettingsStorage provideSettingsStorage(Context context) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideSettingsStorage(context));
  }
}
