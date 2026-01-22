package ai.openpatent.di;

import ai.openpatent.data.remote.api.OrchestratorApi;
import ai.openpatent.data.repository.OrchestratorRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class AppModule_ProvideOrchestratorRepositoryFactory implements Factory<OrchestratorRepository> {
  private final Provider<OrchestratorApi> orchestratorApiProvider;

  public AppModule_ProvideOrchestratorRepositoryFactory(
      Provider<OrchestratorApi> orchestratorApiProvider) {
    this.orchestratorApiProvider = orchestratorApiProvider;
  }

  @Override
  public OrchestratorRepository get() {
    return provideOrchestratorRepository(orchestratorApiProvider.get());
  }

  public static AppModule_ProvideOrchestratorRepositoryFactory create(
      Provider<OrchestratorApi> orchestratorApiProvider) {
    return new AppModule_ProvideOrchestratorRepositoryFactory(orchestratorApiProvider);
  }

  public static OrchestratorRepository provideOrchestratorRepository(
      OrchestratorApi orchestratorApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideOrchestratorRepository(orchestratorApi));
  }
}
