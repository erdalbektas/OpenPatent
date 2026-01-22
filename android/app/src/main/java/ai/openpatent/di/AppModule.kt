package ai.openpatent.di

import android.content.Context
import ai.openpatent.BuildConfig
import ai.openpatent.data.local.SecureTokenStorage
import ai.openpatent.data.local.SettingsStorage
import ai.openpatent.data.remote.api.AuthApi
import ai.openpatent.data.remote.api.BillingApi
import ai.openpatent.data.remote.api.OrchestratorApi
import ai.openpatent.data.remote.api.PatentApi
import ai.openpatent.data.remote.interceptor.AuthInterceptor
import ai.openpatent.data.repository.AuthRepository
import ai.openpatent.data.repository.BillingRepository
import ai.openpatent.data.repository.OrchestratorRepository
import ai.openpatent.data.repository.PatentRepository
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideSecureTokenStorage(
        @ApplicationContext context: Context
    ): SecureTokenStorage = SecureTokenStorage(context)

    @Provides
    @Singleton
    fun provideSettingsStorage(
        @ApplicationContext context: Context
    ): SettingsStorage = SettingsStorage(context)

    @Provides
    @Singleton
    fun provideMoshi(): Moshi = Moshi.Builder()
        .addLast(KotlinJsonAdapterFactory())
        .build()

    @Provides
    @Singleton
    fun provideAuthInterceptor(
        tokenStorage: SecureTokenStorage
    ): AuthInterceptor = AuthInterceptor(tokenStorage)

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }

        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        moshi: Moshi,
        settingsStorage: SettingsStorage
    ): Retrofit {
        val baseUrl = runBlocking { settingsStorage.serverUrl.first() }
        return Retrofit.Builder()
            .baseUrl(baseUrl.trimEnd('/') + "/")
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi = retrofit.create(AuthApi::class.java)

    @Provides
    @Singleton
    fun providePatentApi(retrofit: Retrofit): PatentApi = retrofit.create(PatentApi::class.java)

    @Provides
    @Singleton
    fun provideOrchestratorApi(retrofit: Retrofit): OrchestratorApi = 
        retrofit.create(OrchestratorApi::class.java)

    @Provides
    @Singleton
    fun provideBillingApi(retrofit: Retrofit): BillingApi = retrofit.create(BillingApi::class.java)

    @Provides
    @Singleton
    fun provideAuthRepository(
        authApi: AuthApi,
        tokenStorage: SecureTokenStorage
    ): AuthRepository = AuthRepository(authApi, tokenStorage)

    @Provides
    @Singleton
    fun providePatentRepository(
        patentApi: PatentApi
    ): PatentRepository = PatentRepository(patentApi)

    @Provides
    @Singleton
    fun provideOrchestratorRepository(
        orchestratorApi: OrchestratorApi
    ): OrchestratorRepository = OrchestratorRepository(orchestratorApi)

    @Provides
    @Singleton
    fun provideBillingRepository(
        billingApi: BillingApi
    ): BillingRepository = BillingRepository(billingApi)
}
