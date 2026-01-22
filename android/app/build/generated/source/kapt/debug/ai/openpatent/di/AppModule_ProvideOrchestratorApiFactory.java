package ai.openpatent.di;

import ai.openpatent.data.remote.api.OrchestratorApi;
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
public final class AppModule_ProvideOrchestratorApiFactory implements Factory<OrchestratorApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideOrchestratorApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public OrchestratorApi get() {
    return provideOrchestratorApi(retrofitProvider.get());
  }

  public static AppModule_ProvideOrchestratorApiFactory create(
      Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideOrchestratorApiFactory(retrofitProvider);
  }

  public static OrchestratorApi provideOrchestratorApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideOrchestratorApi(retrofit));
  }
}
