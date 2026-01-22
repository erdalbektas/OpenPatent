package ai.openpatent.ui.home;

import ai.openpatent.data.repository.PatentRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
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
public final class HomeViewModel_Factory implements Factory<HomeViewModel> {
  private final Provider<PatentRepository> patentRepositoryProvider;

  public HomeViewModel_Factory(Provider<PatentRepository> patentRepositoryProvider) {
    this.patentRepositoryProvider = patentRepositoryProvider;
  }

  @Override
  public HomeViewModel get() {
    return newInstance(patentRepositoryProvider.get());
  }

  public static HomeViewModel_Factory create(Provider<PatentRepository> patentRepositoryProvider) {
    return new HomeViewModel_Factory(patentRepositoryProvider);
  }

  public static HomeViewModel newInstance(PatentRepository patentRepository) {
    return new HomeViewModel(patentRepository);
  }
}
