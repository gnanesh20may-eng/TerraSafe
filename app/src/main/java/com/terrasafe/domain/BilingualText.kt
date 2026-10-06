package com.terrasafe.domain

object BilingualText {
    fun getWarningMessage(level: String, location: String, lang: String): String {
        return when (lang.lowercase()) {
            "ta", "tamil" -> when (level) {
                "CRITICAL" -> "கட்டாய எச்சரிக்கை: $location பகுதியில் நிலச்சரிவு அபாயம் மிக அதிகம். உடனடியாக பாதுகாப்பு முகாமிற்கு செல்லவும்."
                "HIGH" -> "எச்சரிக்கை: $location பகுதியில் உயர் அபாயம் கண்டறியப்பட்டுள்ளது. விழிப்புடன் இருக்கவும்."
                "WATCH" -> "கண்காணிப்பு: $location பகுதியில் மழை மற்றும் ஈரப்பதம் அதிகரிக்கிறது."
                else -> "நிலைமை சீராக உள்ளது: $location இயல்பான நிலையில் உள்ளது."
            }
            else -> when (level) {
                "CRITICAL" -> "CRITICAL WARNING: High landslide/flood risk in $location. Evacuate to designated safe zones immediately."
                "HIGH" -> "HIGH RISK ALERT: Elevated environmental hazards detected in $location. Stay alert."
                "WATCH" -> "WATCH ADVISORY: Conditions in $location require monitoring due to rainfall."
                else -> "STABLE: Conditions in $location are within normal parameters."
            }
        }
    }
}
