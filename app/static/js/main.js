// 메인 JavaScript - 성능 최적화된 스크립트

// DOM 로딩 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 모바일 사이드바 토글
    initMobileSidebar();
    
    // 알림 메시지 자동 숨김
    initAlertMessages();
    
    // AJAX 기본 설정
    initAjaxSetup();
    
    // 폼 유효성 검사
    initFormValidation();
    
    // 테이블 기능
    initTableFeatures();
});

// 모바일 사이드바 기능
function initMobileSidebar() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // 사이드바 외부 클릭 시 닫기
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
}

// 알림 메시지 자동 숨김
function initAlertMessages() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        // 성공 메시지는 3초 후 자동 숨김
        if (alert.classList.contains('alert-success')) {
            setTimeout(function() {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            }, 3000);
        }
        
        // 닫기 버튼 추가
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.className = 'alert-close';
        closeBtn.style.cssText = 'float: right; border: none; background: none; font-size: 1.5rem; cursor: pointer;';
        
        closeBtn.addEventListener('click', function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        });
        
        alert.insertBefore(closeBtn, alert.firstChild);
    });
}

// AJAX 기본 설정
function initAjaxSetup() {
    // CSRF 토큰 설정 (향후 CSRF 보호 구현 시)
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        const token = csrfToken.getAttribute('content');
        
        // 모든 AJAX 요청에 CSRF 토큰 포함
        document.addEventListener('ajaxSend', function(event, xhr, settings) {
            xhr.setRequestHeader('X-CSRF-Token', token);
        });
    }
}

// 폼 유효성 검사
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // 필수 입력 필드 검사
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    showFieldError(field, '이 필드는 필수입니다.');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }
            });
            
            // 이메일 형식 검사
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(function(field) {
                if (field.value && !isValidEmail(field.value)) {
                    showFieldError(field, '올바른 이메일 형식을 입력해주세요.');
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

// 필드 오류 표시
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#ea4335';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '4px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#ea4335';
}

// 필드 오류 제거
function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '';
}

// 이메일 유효성 검사
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 테이블 기능 (정렬, 필터링)
function initTableFeatures() {
    const tables = document.querySelectorAll('.table[data-sortable]');
    
    tables.forEach(function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                const currentOrder = this.dataset.order || 'asc';
                const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                
                sortTable(table, column, newOrder);
                
                // 정렬 표시 업데이트
                headers.forEach(h => h.dataset.order = '');
                this.dataset.order = newOrder;
            });
        });
    });
}

// 테이블 정렬
function sortTable(table, column, order) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort(function(a, b) {
        const aVal = a.querySelector(`td[data-value="${column}"]`)?.textContent || '';
        const bVal = b.querySelector(`td[data-value="${column}"]`)?.textContent || '';
        
        if (order === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
    
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

// 유틸리티 함수들
const Utils = {
    // 로딩 표시
    showLoading: function(element) {
        element.innerHTML = '<div class="loading"></div>';
        element.disabled = true;
    },
    
    // 로딩 숨김
    hideLoading: function(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    },
    
    // 알림 표시
    showAlert: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // 3초 후 자동 제거
        setTimeout(function() {
            alertDiv.remove();
        }, 3000);
    },
    
    // API 호출
    apiCall: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .catch(error => {
                console.error('API call error:', error);
                this.showAlert('서버 오류가 발생했습니다.', 'error');
                throw error;
            });
    }
};

// 전역 유틸리티 함수 노출
window.Utils = Utils;