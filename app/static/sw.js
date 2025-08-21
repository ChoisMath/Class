// 서비스 워커 - 기본 구현
// PWA 기능을 원하지 않는 경우 빈 파일로 유지

self.addEventListener('install', function(event) {
    // 설치 시 아무것도 하지 않음
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    // 활성화 시 아무것도 하지 않음
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
    // 네트워크 요청을 그대로 전달
    return;
});