package ai.openpatent.di;

import ai.openpatent.data.remote.api.BillingApi;
import ai.openpatent.data.repository.BillingRepository;
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
public final class AppModule_ProvideBillingRepositoryFactory implements Factory<BillingRepository> {
  private final Provider<BillingApi> billingApiProvider;

  public AppModule_ProvideBillingRepositoryFactory(Provider<BillingApi> billingApiProvider) {
    this.billingApiProvider = billingApiProvider;
  }

  @Override
  public BillingRepository get() {
    return provideBillingRepository(billingApiProvider.get());
  }

  public static AppModule_ProvideBillingRepositoryFactory create(
      Provider<BillingApi> billingApiProvider) {
    return new AppModule_ProvideBillingRepositoryFactory(billingApiProvider);
  }

  public static BillingRepository provideBillingRepository(BillingApi billingApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideBillingRepository(billingApi));
  }
}
