plugins { id("com.android.application") }
android {
    namespace = "com.example.fixture"
    compileSdk = 34
    defaultConfig { minSdk = 24; targetSdk = 34 }
    buildTypes { release { isMinifyEnabled = false } }
}
