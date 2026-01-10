# Study English - Android App

Ứng dụng Android học tiếng Anh sử dụng WebView để kết nối với backend server.

## Yêu cầu

- Android Studio Arctic Fox (2020.3.1) trở lên
- JDK 17
- Android SDK 34
- Gradle 8.2+

## Cài đặt

### 1. Mở project trong Android Studio

```bash
# Mở Android Studio và chọn "Open"
# Điều hướng đến thư mục android/
```

### 2. Cấu hình Backend URL

Chỉnh sửa `BASE_URL` trong `MainActivity.java`:

```java
// Cho Android Emulator (localhost)
private static final String BASE_URL = "http://10.0.2.2:8000";

// Cho thiết bị thật trong mạng LAN
private static final String BASE_URL = "http://192.168.x.x:8000";
```

### 3. Build APK

```bash
# Debug APK
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease
```

APK sẽ được tạo tại:
- Debug: `app/build/outputs/apk/debug/app-debug.apk`
- Release: `app/build/outputs/apk/release/app-release.apk`

## Cấu trúc thư mục

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/studyenglish/
│   │   │   └── MainActivity.java      # Activity chính với WebView
│   │   ├── res/
│   │   │   ├── layout/                 # XML layouts
│   │   │   ├── values/                 # Colors, strings, themes
│   │   │   ├── drawable/               # Icons, backgrounds
│   │   │   └── mipmap-*/               # App icons
│   │   └── AndroidManifest.xml
│   ├── build.gradle                    # App-level dependencies
│   └── proguard-rules.pro
├── build.gradle                        # Project-level config
├── settings.gradle
└── gradle.properties
```

## Tính năng Native

### JavaScript Bridge

Web app có thể gọi các tính năng Android thông qua `AndroidBridge`:

```javascript
// Text-to-Speech
AndroidBridge.speak("Hello, how are you?");
AndroidBridge.speak("Xin chào", "vi-VN");

// Toast message
AndroidBridge.showToast("Thông báo!");

// Device info
const info = AndroidBridge.getDeviceInfo();
```

### Permissions

- `INTERNET` - Kết nối mạng
- `ACCESS_NETWORK_STATE` - Kiểm tra trạng thái mạng
- `RECORD_AUDIO` - Ghi âm (cho tính năng phát âm)

## Chạy Backend

Trước khi chạy app, cần khởi động backend server:

```bash
cd ../web/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Không kết nối được đến server

1. Kiểm tra backend đang chạy
2. Kiểm tra `BASE_URL` đúng
3. Với emulator: sử dụng `10.0.2.2` thay vì `localhost`
4. Với thiết bị thật: đảm bảo cùng mạng WiFi

### WebView blank trắng

1. Kiểm tra `android:usesCleartextTraffic="true"` trong AndroidManifest
2. Kiểm tra permissions INTERNET
