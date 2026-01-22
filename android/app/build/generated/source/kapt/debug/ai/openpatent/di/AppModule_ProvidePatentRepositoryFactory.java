package ai.openpatent.di;

import ai.openpatent.data.remote.api.PatentApi;
import ai.openpatent.data.repository.PatentRepository;
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
public final class AppModule_ProvidePatentRepositoryFactory implements Factory<PatentRepository> {
  private final Provider<PatentApi> patentApiProvider;

  public AppModule_ProvidePatentRepositoryFactory(Provider<PatentApi> patentApiProvider) {
    this.patentApiProvider = patentApiProvider;
  }

  @Override
  public PatentRepository get() {
    return providePatentRepository(patentApiProvider.get());
  }

  public static AppModule_ProvidePatentRepositoryFactory create(
      Provider<PatentApi> patentApiProvider) {
    return new AppModule_ProvidePatentRepositoryFactory(patentApiProvider);
  }

  public static PatentRepository providePatentRepository(PatentApi patentApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.providePatentRepository(patentApi));
  }
}
