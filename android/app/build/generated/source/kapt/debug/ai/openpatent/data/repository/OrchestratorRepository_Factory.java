package ai.openpatent.data.repository;

import ai.openpatent.data.remote.api.OrchestratorApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class OrchestratorRepository_Factory implements Factory<OrchestratorRepository> {
  private final Provider<OrchestratorApi> orchestratorApiProvider;

  public OrchestratorRepository_Factory(Provider<OrchestratorApi> orchestratorApiProvider) {
    this.orchestratorApiProvider = orchestratorApiProvider;
  }

  @Override
  public OrchestratorRepository get() {
    return newInstance(orchestratorApiProvider.get());
  }

  public static OrchestratorRepository_Factory create(
      Provider<OrchestratorApi> orchestratorApiProvider) {
    return new OrchestratorRepository_Factory(orchestratorApiProvider);
  }

  public static OrchestratorRepository newInstance(OrchestratorApi orchestratorApi) {
    return new OrchestratorRepository(orchestratorApi);
  }
}
