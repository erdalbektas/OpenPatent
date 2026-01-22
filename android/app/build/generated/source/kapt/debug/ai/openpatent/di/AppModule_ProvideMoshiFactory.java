package ai.openpatent.di;

import com.squareup.moshi.Moshi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class AppModule_ProvideMoshiFactory implements Factory<Moshi> {
  @Override
  public Moshi get() {
    return provideMoshi();
  }

  public static AppModule_ProvideMoshiFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static Moshi provideMoshi() {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideMoshi());
  }

  private static final class InstanceHolder {
    private static final AppModule_ProvideMoshiFactory INSTANCE = new AppModule_ProvideMoshiFactory();
  }
}
