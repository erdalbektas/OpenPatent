package ai.openpatent.di;

import ai.openpatent.data.remote.api.PatentApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import retrofit2.Retrofit;

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
public final class AppModule_ProvidePatentApiFactory implements Factory<PatentApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvidePatentApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public PatentApi get() {
    return providePatentApi(retrofitProvider.get());
  }

  public static AppModule_ProvidePatentApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvidePatentApiFactory(retrofitProvider);
  }

  public static PatentApi providePatentApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.providePatentApi(retrofit));
  }
}
