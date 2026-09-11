package com.example.fixture

import android.content.Context

class TokenStore(private val ctx: Context) {
    fun save(token: String) {
        ctx.getSharedPreferences("auth", Context.MODE_PRIVATE)
            .edit().putString("bearer", token).apply()
    }

    // NEGATIVE: non-sensitive UI state in SharedPreferences is fine
    fun saveLastTab(index: Int) {
        ctx.getSharedPreferences("ui", Context.MODE_PRIVATE)
            .edit().putInt("last_tab", index).apply()
    }
}
