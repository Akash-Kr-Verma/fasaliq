package com.fasaliq.app

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.LoginRequest
import com.fasaliq.app.ui.auth.RegisterActivity
import com.fasaliq.app.ui.buyer.BuyerDashboardActivity
import com.fasaliq.app.ui.farmer.FarmerDashboardActivity
import com.fasaliq.app.utils.SessionManager
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var session: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        session = SessionManager(this)

        if (session.isLoggedIn()) {
            navigateByRole(session.getRole())
            return
        }

        setContentView(R.layout.activity_main)

        val etPhone = findViewById<EditText>(R.id.etPhone)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val btnLogin = findViewById<Button>(R.id.btnLogin)
        val btnGoRegister = findViewById<Button>(R.id.btnGoRegister)
        val tvError = findViewById<TextView>(R.id.tvError)

        btnLogin.setOnClickListener {
            val phone = etPhone.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (phone.isEmpty() || password.isEmpty()) {
                tvError.text = "Please enter phone and password"
                return@setOnClickListener
            }

            btnLogin.isEnabled = false
            btnLogin.text = "Logging in..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance.login(
                        LoginRequest(phone, password)
                    )
                    if (response.isSuccessful) {
                        val body = response.body()!!
                        session.saveSession(
                            body.access_token,
                            body.user_id,
                            body.role,
                            body.name
                        )
                        tvError.text = ""
                        navigateByRole(body.role)
                    } else {
                        tvError.text = "Invalid phone or password"
                        btnLogin.isEnabled = true
                        btnLogin.text = "Login"
                    }
                } catch (e: Exception) {
                    tvError.text = "Cannot connect to server. Is it running?"
                    btnLogin.isEnabled = true
                    btnLogin.text = "Login"
                }
            }
        }

        btnGoRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }
    }

    private fun navigateByRole(role: String?) {
        val intent = when (role) {
            "farmer" -> Intent(this, FarmerDashboardActivity::class.java)
            "buyer" -> Intent(this, BuyerDashboardActivity::class.java)
            else -> Intent(this, FarmerDashboardActivity::class.java)
        }
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}