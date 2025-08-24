/**
 * DSHS-Life Style Seating Manager
 * 자리배치표 관리 JavaScript (DSHS-Life 스타일)
 */

class SeatingManager {
    constructor(config) {
        this.isTeacher = config.isTeacher || false;
        this.userId = config.userId;
        this.userName = config.userName;
        
        // 상태 변수들
        this.currentDate = null;
        this.currentGrade = 1;
        this.currentPeriod = 11; // 기본값: 1차자습
        this.periods = [];
        this.gradeSeats = [];
        this.selectedStudents = new Set();
        this.selectionMode = false;
        
        // DOM 요소들
        this.elements = {};
        
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.setupEventListeners();
        this.initializeDate();
        this.loadPeriods();
        this.loadSeatingData();
    }
    
    cacheElements() {
        this.elements = {
            datePicker: document.getElementById('date-picker'),
            gradeSelect: document.getElementById('grade-select'),
            periodSelect: document.getElementById('period-select'),
            periodPrev: document.getElementById('period-prev'),
            periodNext: document.getElementById('period-next'),
            seatGrid: document.getElementById('seat-grid'),
            loadingIndicator: document.getElementById('loading-indicator'),
            selectionMode: document.getElementById('selection-mode'),
            selectedCount: document.getElementById('selected-count'),
            markAbsent: document.getElementById('mark-absent'),
            markPresent: document.getElementById('mark-present'),
            modal: document.getElementById('student-modal'),
            modalTitle: document.getElementById('modal-title'),
            modalBody: document.getElementById('modal-body'),
            modalClose: document.getElementById('modal-close'),
            notification: document.getElementById('notification'),
            notificationMessage: document.getElementById('notification-message'),
            notificationClose: document.getElementById('notification-close')
        };
    }
    
    setupEventListeners() {
        // 날짜/학년/교시 변경 이벤트
        this.elements.datePicker?.addEventListener('change', () => {
            this.currentDate = this.elements.datePicker.value;
            this.loadPeriods();
            this.clearSelection();
        });
        
        this.elements.gradeSelect?.addEventListener('change', () => {
            this.currentGrade = parseInt(this.elements.gradeSelect.value);
            this.loadSeatingData();
            this.clearSelection();
        });
        
        this.elements.periodSelect?.addEventListener('change', () => {
            this.currentPeriod = parseInt(this.elements.periodSelect.value);
            this.loadSeatingData();
            this.clearSelection();
        });
        
        // 교시 이전/다음 버튼
        this.elements.periodPrev?.addEventListener('click', () => this.changePeriod(-1));
        this.elements.periodNext?.addEventListener('click', () => this.changePeriod(1));
        
        // 선택 모드 토글
        this.elements.selectionMode?.addEventListener('change', (e) => {
            this.selectionMode = e.target.checked;
            this.clearSelection();
            this.updateSelectionUI();
        });
        
        // 부재/복귀 버튼
        this.elements.markAbsent?.addEventListener('click', () => this.markAttendance('absent'));
        this.elements.markPresent?.addEventListener('click', () => this.markAttendance('present'));
        
        // 모달 관련
        this.elements.modalClose?.addEventListener('click', () => this.closeModal());
        this.elements.modal?.addEventListener('click', (e) => {
            if (e.target === this.elements.modal) this.closeModal();
        });
        
        // 알림 닫기
        this.elements.notificationClose?.addEventListener('click', () => this.hideNotification());
        
        // 키보드 단축키
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // ESC 키로 선택 해제
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearSelection();
                this.closeModal();
            }
        });
    }
    
    initializeDate() {
        const today = new Date().toISOString().split('T')[0];
        if (this.elements.datePicker) {
            this.elements.datePicker.value = today;
            this.currentDate = today;
        }
    }
    
    async loadPeriods() {
        if (!this.currentDate) return;
        
        try {
            const response = await fetch(`/seating/api/periods/${this.currentDate}`);
            const data = await response.json();
            
            if (data.success) {
                this.periods = data.periods;
                this.updatePeriodSelect();
            }
        } catch (error) {
            console.error('교시 정보 로드 실패:', error);
        }
    }
    
    updatePeriodSelect() {
        if (!this.elements.periodSelect) return;
        
        const periodNames = {
            1: '1교시', 2: '2교시', 3: '3교시', 4: '4교시',
            5: '5교시', 6: '6교시', 7: '7교시',
            11: '1차자습', 12: '2차자습', 13: '3차자습', 
            14: '4차자습', 15: '5차자습',
            22: '중식', 23: '석식'
        };
        
        this.elements.periodSelect.innerHTML = '';
        
        this.periods.forEach(period => {
            const option = document.createElement('option');
            option.value = period;
            option.textContent = periodNames[period] || `${period}교시`;
            this.elements.periodSelect.appendChild(option);
        });
        
        // 현재 교시 선택
        if (this.periods.includes(this.currentPeriod)) {
            this.elements.periodSelect.value = this.currentPeriod;
        } else if (this.periods.length > 0) {
            this.currentPeriod = this.periods[0];
            this.elements.periodSelect.value = this.currentPeriod;
        }
    }
    
    changePeriod(direction) {
        const currentIndex = this.periods.indexOf(this.currentPeriod);
        let newIndex = currentIndex + direction;
        
        if (newIndex < 0) newIndex = this.periods.length - 1;
        if (newIndex >= this.periods.length) newIndex = 0;
        
        this.currentPeriod = this.periods[newIndex];
        this.elements.periodSelect.value = this.currentPeriod;
        this.loadSeatingData();
        this.clearSelection();
    }
    
    /**
     * 자리배치 데이터 로드
     */
    async loadSeatArrangement() {
        if (!this.elements.seatGrid) return;
        
        this.showLoading();
        
        try {
            const response = await fetch('/seating/api/seat-arrangement', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: this.currentDate,
                    period: this.currentPeriod,
                    grade: this.currentGrade
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.gradeSeats = data.grade_seats || [];
                this.renderSeatingChart();
            } else {
                this.showNotification('자리배치 데이터 로드 실패: ' + (data.error || '알 수 없는 오류'), 'error');
            }
        } catch (error) {
            console.error('자리배치 데이터 로드 실패:', error);
            this.showNotification('서버 연결 실패', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    renderSeatingChart() {
        if (!this.elements.seatGrid) return;
        
        const gridHtml = this.gradeSeats.map(grade => {
            const sectionsHtml = grade.seats.map(section => this.createSection(section)).join('');
            
            return `
                <div class="grade-container">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">${grade.name}</h3>
                    <div class="sections-container flex gap-1">
                        ${sectionsHtml}
                    </div>
                    ${grade.bottom_left ? `
                        <div class="inline-block px-2 py-3 mt-4 text-sm font-semibold border-2 border-gray-500">
                            ${grade.bottom_left}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        this.elements.seatGrid.innerHTML = gridHtml;
        
        // 좌석 클릭 이벤트 설정
        this.setupSeatClickHandlers();
    }
    
    createSection(section) {
        const seatItems = this.createSeatItems(section);
        const borderClass = section.stick ? 'border-l-4 border-gray-800' : '';
        
        return `
            <div class="seat-section ${borderClass}">
                <div class="section-header text-center text-sm font-medium text-gray-700 mb-1">
                    ${section.name}
                </div>
                <div class="seat-columns flex">
                    ${section.cols > 1 ? this.createDoubleColumn(seatItems) : this.createSingleColumn(seatItems)}
                </div>
            </div>
        `;
    }
    
    createSeatItems(section) {
        // DSHS-Life의 seatLine 함수 구현
        const items = [];
        
        if (section.type === 'single') {
            // 단일 열 좌석 (7개)
            for (let i = 0; i < 7; i++) {
                items.push(this.createEmptySeat());
            }
        } else {
            // 이중 열 좌석 (좌우 각 7개)
            const leftSeats = [];
            const rightSeats = [];
            
            for (let i = 0; i < 7; i++) {
                leftSeats.push(this.createEmptySeat());
                rightSeats.push(this.createEmptySeat());
            }
            
            items.push({ left: leftSeats, right: rightSeats });
        }
        
        return items;
    }
    
    createEmptySeat() {
        return {
            user: null,
            items: []
        };
    }
    
    createSingleColumn(seatItems) {
        const seatsHtml = seatItems.map((seat, index) => this.createSeatElement(seat, index)).join('');
        return `<div class="single-column">${seatsHtml}</div>`;
    }
    
    createDoubleColumn(seatItems) {
        if (seatItems.length > 0 && seatItems[0].left) {
            const leftHtml = seatItems[0].left.map((seat, index) => this.createSeatElement(seat, `L${index}`)).join('');
            const rightHtml = seatItems[0].right.map((seat, index) => this.createSeatElement(seat, `R${index}`)).join('');
            
            return `
                <div class="double-column flex gap-1">
                    <div class="left-seats">${leftHtml}</div>
                    <div class="right-seats">${rightHtml}</div>
                </div>
            `;
        }
        
        return '<div class="double-column"></div>';
    }
    
    createSeatElement(seat, position) {
        const isEmpty = !seat.user;
        const user = seat.user;
        const activities = seat.items || [];
        
        let statusClass = 'seat-empty';
        let bgColor = 'bg-gray-100';
        
        if (!isEmpty) {
            if (activities.length > 0) {
                statusClass = 'seat-activity';
                bgColor = 'bg-blue-100';
            } else {
                statusClass = 'seat-present';
                bgColor = 'bg-white';
            }
        }
        
        const isSelected = user && this.selectedStudents.has(user.email);
        const selectedClass = isSelected ? 'ring-2 ring-yellow-400 bg-yellow-100' : '';
        
        const activityText = activities.length > 0 ? activities[0].place || activities[0].type : '';
        
        return `
            <div class="seat-item ${statusClass} ${selectedClass} ${bgColor} border border-gray-300 cursor-pointer 
                        flex flex-col justify-center items-center text-xs p-1 min-w-[60px] min-h-[60px]"
                 data-position="${position}"
                 data-user-email="${user?.email || ''}"
                 data-user-name="${user?.name || ''}"
                 data-user-no="${user?.no || ''}">
                
                ${!isEmpty ? `
                    <div class="text-xs text-gray-600">${user.no}</div>
                    <div class="font-medium text-center leading-tight">${user.name}</div>
                    ${activityText ? `<div class="text-xs text-blue-600 text-center">${activityText}</div>` : ''}
                ` : ''}
            </div>
        `;
    }
    
    setupSeatClickHandlers() {
        const seatElements = this.elements.seatGrid.querySelectorAll('.seat-item');
        
        seatElements.forEach(seatEl => {
            seatEl.addEventListener('click', (e) => this.handleSeatClick(e, seatEl));
        });
    }
    
    showLoading(show) {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.classList.toggle('hidden', !show);
        }
    }
    
    handleSeatClick(e, seatEl) {
        const userEmail = seatEl.dataset.userEmail;
        const userName = seatEl.dataset.userName;
        const userNo = seatEl.dataset.userNo;
        
        if (!userEmail) return; // 빈 자리
        
        if (this.selectionMode && this.isTeacher) {
            // 선택 모드: 학생 선택/해제
            this.toggleStudentSelection(userEmail, seatEl);
        } else {
            // 일반 모드: 학생 정보 모달 표시
            this.showStudentModal(userEmail, userName, userNo);
        }
    }
    
    toggleStudentSelection(userEmail, seatEl) {
        if (this.selectedStudents.has(userEmail)) {
            this.selectedStudents.delete(userEmail);
            seatEl.classList.remove('ring-2', 'ring-yellow-400', 'bg-yellow-100');
        } else {
            this.selectedStudents.add(userEmail);
            seatEl.classList.add('ring-2', 'ring-yellow-400', 'bg-yellow-100');
        }
        
        this.updateSelectionCount();
        this.updateAttendanceButtons();
    }
    
    clearSelection() {
        this.selectedStudents.clear();
        
        // UI에서 선택 표시 제거
        const selectedElements = this.elements.seatGrid.querySelectorAll('.ring-2');
        selectedElements.forEach(el => {
            el.classList.remove('ring-2', 'ring-yellow-400', 'bg-yellow-100');
        });
        
        this.updateSelectionCount();
        this.updateAttendanceButtons();
    }
    
    updateSelectionUI() {
        const buttons = [this.elements.markAbsent, this.elements.markPresent];
        buttons.forEach(btn => {
            if (btn) {
                btn.disabled = !this.selectionMode;
                btn.style.opacity = this.selectionMode ? '1' : '0.5';
            }
        });
    }
    
    updateSelectionCount() {
        if (this.elements.selectedCount) {
            this.elements.selectedCount.textContent = `(${this.selectedStudents.size}명)`;
        }
    }
    
    updateAttendanceButtons() {
        const hasSelection = this.selectedStudents.size > 0;
        
        if (this.elements.markAbsent) {
            this.elements.markAbsent.disabled = !hasSelection;
        }
        if (this.elements.markPresent) {
            this.elements.markPresent.disabled = !hasSelection;
        }
    }
    
    async markAttendance(status) {
        if (this.selectedStudents.size === 0) {
            this.showNotification('학생을 선택해주세요.', 'warning');
            return;
        }
        
        const studentEmails = Array.from(this.selectedStudents);
        const statusText = status === 'absent' ? '부재' : '복귀';
        
        if (!confirm(`선택한 ${studentEmails.length}명의 학생을 ${statusText} 처리하시겠습니까?`)) {
            return;
        }
        
        try {
            const response = await fetch('/seating/api/mark-attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: this.currentDate,
                    period: this.currentPeriod,
                    student_emails: studentEmails,
                    status: status
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`${data.affected_count}명의 학생을 ${statusText} 처리했습니다.`, 'success');
                this.clearSelection();
                this.loadSeatingData(); // 새로고침
            } else {
                this.showNotification('출석 처리 실패: ' + (data.error || '알 수 없는 오류'), 'error');
            }
        } catch (error) {
            console.error('출석 처리 실패:', error);
            this.showNotification('서버 연결 실패', 'error');
        }
    }
    
    showStudentModal(userEmail, userName, userNo) {
        if (!this.elements.modal) return;
        
        this.elements.modalTitle.textContent = `${userName} (${userNo})`;
        this.elements.modalBody.innerHTML = `
            <div class="space-y-2">
                <p><strong>이메일:</strong> ${userEmail}</p>
                <p><strong>학번:</strong> ${userNo}</p>
                <p><strong>이름:</strong> ${userName}</p>
                <p><strong>날짜:</strong> ${this.currentDate}</p>
                <p><strong>교시:</strong> ${this.currentPeriod}</p>
            </div>
        `;
        
        this.elements.modal.classList.add('show');
    }
    
    closeModal() {
        if (this.elements.modal) {
            this.elements.modal.classList.remove('show');
        }
    }
    
    showNotification(message, type = 'info') {
        if (!this.elements.notification) return;
        
        this.elements.notificationMessage.textContent = message;
        this.elements.notification.className = `notification show ${type}`;
        
        // 자동 닫기 (5초)
        setTimeout(() => {
            this.hideNotification();
        }, 5000);
    }
    
    hideNotification() {
        if (this.elements.notification) {
            this.elements.notification.classList.remove('show');
        }
    }
    
    handleKeyboard(e) {
        // Ctrl + R: 새로고침
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            this.loadSeatingData();
        }
        
        // Ctrl + S: 선택 모드 토글
        if (e.ctrlKey && e.key === 's' && this.isTeacher) {
            e.preventDefault();
            if (this.elements.selectionMode) {
                this.elements.selectionMode.checked = !this.elements.selectionMode.checked;
                this.selectionMode = this.elements.selectionMode.checked;
                this.clearSelection();
                this.updateSelectionUI();
            }
        }
    }
    
    // 유틸리티 메서드들
    formatDate(date) {
        return new Date(date).toLocaleDateString('ko-KR');
    }
    
    formatPeriod(period) {
        const periodNames = {
            1: '1교시', 2: '2교시', 3: '3교시', 4: '4교시',
            5: '5교시', 6: '6교시', 7: '7교시',
            11: '1차자습', 12: '2차자습', 13: '3차자습', 
            14: '4차자습', 15: '5차자습',
            22: '중식', 23: '석식'
        };
        
        return periodNames[period] || `${period}교시`;
    }
}

// 전역 접근을 위한 내보내기
window.SeatingManager = SeatingManager;