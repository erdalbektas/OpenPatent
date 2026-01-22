package ai.openpatent.data.repository;

import ai.openpatent.data.remote.api.BillingApi;
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
public final class BillingRepository_Factory implements Factory<BillingRepository> {
  private final Provider<BillingApi> billingApiProvider;

  public BillingRepository_Factory(Provider<BillingApi> billingApiProvider) {
    this.billingApiProvider = billingApiProvider;
  }

  @Override
  public BillingRepository get() {
    return newInstance(billingApiProvider.get());
  }

  public static BillingRepository_Factory create(Provider<BillingApi> billingApiProvider) {
    return new BillingRepository_Factory(billingApiProvider);
  }

  public static BillingRepository newInstance(BillingApi billingApi) {
    return new BillingRepository(billingApi);
  }
}
