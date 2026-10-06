# ProGuard rules for TerraSafe Room and Serialization
-keepattributes *Annotation*,Signature,EnclosingMethod
-keepclassmembers class * {
    @androidx.room.* <methods>;
}
-keep class androidx.room.** { *; }
-dontwarn androidx.room.**
-keep class kotlinx.serialization.** { *; }
