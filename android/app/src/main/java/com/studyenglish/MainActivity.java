package com.studyenglish;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.util.Locale;

/**
 * MainActivity - Ứng dụng học tiếng Anh
 * Sử dụng WebView để load giao diện web và tích hợp các tính năng native Android
 */
public class MainActivity extends AppCompatActivity implements TextToSpeech.OnInitListener {

    private WebView webView;
    private ProgressBar progressBar;
    private TextToSpeech textToSpeech;

    // URL của backend server (thay đổi tùy theo môi trường)
    private static final String BASE_URL = "http://10.0.2.2:8000"; // Android emulator localhost
    // private static final String BASE_URL = "http://192.168.x.x:8000"; // Local network

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize views
        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);

        // Initialize Text-to-Speech
        textToSpeech = new TextToSpeech(this, this);

        // Setup WebView
        setupWebView();

        // Load the web app
        webView.loadUrl(BASE_URL);
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();

        // Enable JavaScript
        webSettings.setJavaScriptEnabled(true);

        // Enable DOM storage
        webSettings.setDomStorageEnabled(true);

        // Enable database
        webSettings.setDatabaseEnabled(true);

        // Enable caching
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setAppCacheEnabled(true);

        // Enable zoom
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);

        // Responsive design
        webSettings.setUseWideViewPort(true);
        webSettings.setLoadWithOverviewMode(true);

        // Allow mixed content (HTTP + HTTPS)
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        // Enable file access
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);

        // Add JavaScript interface for native features
        webView.addJavascriptInterface(new AndroidBridge(), "AndroidBridge");

        // WebViewClient to handle page loading
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // Handle external links
                if (url.startsWith("http://") || url.startsWith("https://")) {
                    if (url.contains("10.0.2.2") || url.contains("localhost") || url.contains("192.168")) {
                        return false; // Load in WebView
                    } else {
                        // Open external links in browser
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    }
                }
                return false;
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                super.onReceivedError(view, errorCode, description, failingUrl);
                // Show error page or toast
                Toast.makeText(MainActivity.this,
                    "Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.",
                    Toast.LENGTH_LONG).show();
            }
        });

        // WebChromeClient for progress and console
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                super.onProgressChanged(view, newProgress);
                progressBar.setProgress(newProgress);
            }
        });
    }

    /**
     * JavaScript Bridge - Cho phép web app gọi các tính năng native Android
     */
    public class AndroidBridge {

        @JavascriptInterface
        public void speak(String text) {
            speak(text, "en-US");
        }

        @JavascriptInterface
        public void speak(String text, String language) {
            if (textToSpeech != null) {
                Locale locale = language.startsWith("vi") ? new Locale("vi", "VN") : Locale.US;
                textToSpeech.setLanguage(locale);
                textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
            }
        }

        @JavascriptInterface
        public void showToast(String message) {
            runOnUiThread(() -> Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface
        public void vibrate(int duration) {
            // Add vibration if needed
        }

        @JavascriptInterface
        public String getDeviceInfo() {
            return android.os.Build.MODEL + " - Android " + android.os.Build.VERSION.RELEASE;
        }
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            textToSpeech.setLanguage(Locale.US);
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (textToSpeech != null) {
            textToSpeech.stop();
            textToSpeech.shutdown();
        }
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.onPause();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }
}
