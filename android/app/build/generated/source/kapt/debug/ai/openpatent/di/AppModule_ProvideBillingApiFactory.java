package ai.openpatent.di;

import ai.openpatent.data.remote.api.BillingApi;
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
public final class AppModule_ProvideBillingApiFactory implements Factory<BillingApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideBillingApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public BillingApi get() {
    return provideBillingApi(retrofitProvider.get());
  }

  public static AppModule_ProvideBillingApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideBillingApiFactory(retrofitProvider);
  }

  public static BillingApi provideBillingApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideBillingApi(retrofit));
  }
}
