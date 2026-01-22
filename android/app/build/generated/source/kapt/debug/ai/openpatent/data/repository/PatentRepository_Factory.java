package ai.openpatent.data.repository;

import ai.openpatent.data.remote.api.PatentApi;
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
public final class PatentRepository_Factory implements Factory<PatentRepository> {
  private final Provider<PatentApi> patentApiProvider;

  public PatentRepository_Factory(Provider<PatentApi> patentApiProvider) {
    this.patentApiProvider = patentApiProvider;
  }

  @Override
  public PatentRepository get() {
    return newInstance(patentApiProvider.get());
  }

  public static PatentRepository_Factory create(Provider<PatentApi> patentApiProvider) {
    return new PatentRepository_Factory(patentApiProvider);
  }

  public static PatentRepository newInstance(PatentApi patentApi) {
    return new PatentRepository(patentApi);
  }
}
