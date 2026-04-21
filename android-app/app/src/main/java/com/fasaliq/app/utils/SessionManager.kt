package com.fasaliq.app.utils

import android.content.Context
import android.content.SharedPreferences

class SessionManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("FasalIQ", Context.MODE_PRIVATE)

    fun saveSession(
        token: String,
        userId: Int,
        role: String,
        name: String
    ) {
        prefs.edit().apply {
            putString(Constants.PREF_TOKEN, token)
            putInt(Constants.PREF_USER_ID, userId)
            putString(Constants.PREF_ROLE, role)
            putString(Constants.PREF_NAME, name)
            apply()
        }
    }

    fun getToken(): String? =
        prefs.getString(Constants.PREF_TOKEN, null)

    fun getUserId(): Int =
        prefs.getInt(Constants.PREF_USER_ID, -1)

    fun getRole(): String? =
        prefs.getString(Constants.PREF_ROLE, null)

    fun getName(): String? =
        prefs.getString(Constants.PREF_NAME, null)

    fun isLoggedIn(): Boolean = getToken() != null

    fun clearSession() = prefs.edit().clear().apply()

    fun getBearerToken(): String = "Bearer ${getToken()}"
}