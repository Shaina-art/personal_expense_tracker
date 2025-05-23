package com.yourapp.sms

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.telephony.SmsMessage
import android.provider.Telephony
import android.content.BroadcastReceiver
import android.content.Context
import android.content.IntentFilter
import kotlinx.coroutines.*
import com.yourapp.network.ApiClient
import com.yourapp.utils.Notifier.showNotification

class SmsService : Service() {

    private val smsReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (Telephony.Sms.Intents.SMS_RECEIVED_ACTION == intent.action) {
                for (sms in Telephony.Sms.Intents.getMessagesFromIntent(intent)) {
                    val sender = sms.displayOriginatingAddress
                    val message = sms.messageBody

                    CoroutineScope(Dispatchers.IO).launch {
                        try {
                            val response = ApiClient.api.parseSms(sender, message)
                            response.alerts?.forEach {
                                showNotification(context, "💡 Reminder Alert", it)
                            }
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                }
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        val filter = IntentFilter(Telephony.Sms.Intents.SMS_RECEIVED_ACTION)
        filter.priority = IntentFilter.SYSTEM_HIGH_PRIORITY
        registerReceiver(smsReceiver, filter)
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(smsReceiver)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
