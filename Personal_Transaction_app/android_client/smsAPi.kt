package <your_package_name>.network

import retrofit2.http.Body
import retrofit2.http.POST

data class SmsRequest(val sender: String, val message: String)
data class SmsResponse(val status: String, val alerts: List<String>?)

interface SmsApi {
    @POST("sms/parse")
    suspend fun parseSms(@Body request: SmsRequest): SmsResponse
}
