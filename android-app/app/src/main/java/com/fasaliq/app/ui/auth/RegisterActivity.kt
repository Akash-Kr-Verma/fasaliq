package com.fasaliq.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.fasaliq.app.MainActivity
import com.fasaliq.app.R
import com.fasaliq.app.api.RetrofitClient
import com.fasaliq.app.models.RegisterRequest
import kotlinx.coroutines.launch
import org.json.JSONObject

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val etName = findViewById<EditText>(R.id.etName)
        val etPhone = findViewById<EditText>(R.id.etPhone)
        val etEmail = findViewById<EditText>(R.id.etEmail)
        val etPassword = findViewById<EditText>(R.id.etPassword)
        val etDistrict = findViewById<EditText>(R.id.etDistrict)
        val rgRole = findViewById<RadioGroup>(R.id.rgRole)
        val rbFarmer = findViewById<RadioButton>(R.id.rbFarmer)
        val btnRegister = findViewById<Button>(R.id.btnRegister)
        val btnBackLogin = findViewById<Button>(R.id.btnBackLogin)
        val tvError = findViewById<TextView>(R.id.tvError)

        btnRegister.setOnClickListener {
            val name = etName.text.toString().trim()
            val phone = etPhone.text.toString().trim()
            val email = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()
            val district = etDistrict.text.toString().trim()
            val role = if (rgRole.checkedRadioButtonId
                == rbFarmer.id) "farmer" else "buyer"

            if (name.isEmpty() || phone.isEmpty() ||
                password.isEmpty() || district.isEmpty()) {
                tvError.text = "Please fill all required fields"
                return@setOnClickListener
            }

            if (password.length < 6) {
                tvError.text = "Password must be at least 6 characters"
                return@setOnClickListener
            }

            btnRegister.isEnabled = false
            btnRegister.text = "Creating account..."

            lifecycleScope.launch {
                try {
                    val response = RetrofitClient.instance.register(
                        RegisterRequest(
                            name = name,
                            phone = phone,
                            email = email.ifEmpty { null },
                            password = password,
                            role = role,
                            district = district
                        )
                    )
                    if (response.isSuccessful) {
                        Toast.makeText(
                            this@RegisterActivity,
                            "Account created! Please login.",
                            Toast.LENGTH_LONG
                        ).show()
                        startActivity(
                            Intent(this@RegisterActivity,
                                MainActivity::class.java)
                        )
                        finish()
                    } else {
                        val errorBody = response.errorBody()?.string()
                        val errorMessage = try {
                            JSONObject(errorBody).getString("detail")
                        } catch (e: Exception) {
                            "Registration failed"
                        }
                        tvError.text = errorMessage
                        btnRegister.isEnabled = true
                        btnRegister.text = "Create Account"
                    }
                } catch (e: Exception) {
                    tvError.text = "Cannot connect to server"
                    btnRegister.isEnabled = true
                    btnRegister.text = "Create Account"
                }
            }
        }

        btnBackLogin.setOnClickListener {
            finish()
        }
    }
}