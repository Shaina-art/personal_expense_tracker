package <your_package_name>.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import <your_package_name>.utils.showNotification
import kotlinx.coroutines.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class SmsReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Assuming you've parsed sender & message from SMS
        val sender = "JD-SBI" // Example
        val message = "Your a/c is debited with INR 100.00 on 15-05-2025..."

        CoroutineScope(Dispatchers.IO).launch {
            val response = sendToApi(sender, message)

            response.alerts?.forEach {
                withContext(Dispatchers.Main) {
                    showNotification(context, "💡 Reminder Alert", it)
                }
            }
        }
    }

    suspend fun sendToApi(sender: String, message: String): SmsResponse {
        val retrofit = Retrofit.Builder()
            .baseUrl("http://<your_ip>:8000/") // Replace with FastAPI backend
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        val api = retrofit.create(SmsApi::class.java)
        return api.parseSms(SmsRequest(sender, message))
    }
}
