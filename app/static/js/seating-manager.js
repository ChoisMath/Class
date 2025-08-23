/**
 * 자리배치 관리 시스템 JavaScript
 * DSHS-Life 시스템을 참고하여 구현
 */

class SeatingManager {
    constructor(options = {}) {
        this.options = {
            isTeacher: false,
            userId: null,
            userName: null,
            ...options
        };
        
        // 상태 관리
        this.selectedStudents = new Set();
        this.selectionMode = false;
        this.currentDate = null;
        this.currentPeriod = null;
        this.currentGrade = 1;
        this.seatData = null;
        
        // DOM 요소
        this.elements = {};
        
        // 이벤트 리스너 초기화
        this.initializeElements();
        this.initializeEventListeners();
        this.loadInitialData();
        
        console.log('SeatingManager initialized', this.options);
    }
    
    /**
     * DOM 요소 초기화
     */
    initializeElements() {
        this.elements = {
            datePicker: document.getElementById('date-picker'),
            gradeSelect: document.getElementById('grade-select'),
            periodSelect: document.getElementById('period-select'),
            loadDataBtn: document.getElementById('load-data'),
            refreshBtn: document.getElementById('refresh-data'),
            seatGrid: document.getElementById('seat-grid'),
            classroomTitle: document.getElementById('classroom-title'),
            selectionModeToggle: document.getElementById('selection-mode'),
            markAbsentBtn: document.getElementById('mark-absent'),
            markPresentBtn: document.getElementById('mark-present'),
            selectedCount: document.getElementById('selected-count'),
            recentChanges: document.getElementById('recent-changes'),
            modal: document.getElementById('student-modal'),
            notification: document.getElementById('notification')
        };
    }
    
    /**
     * 이벤트 리스너 초기화
     */
    initializeEventListeners() {
        // 컨트롤 이벤트
        if (this.elements.datePicker) {
            this.elements.datePicker.addEventListener('change', () => this.updateCurrentDate());
        }
        
        if (this.elements.gradeSelect) {
            this.elements.gradeSelect.addEventListener('change', () => this.updateCurrentGrade());
        }
        
        if (this.elements.periodSelect) {
            this.elements.periodSelect.addEventListener('change', () => this.updateCurrentPeriod());
        }
        
        if (this.elements.loadDataBtn) {
            this.elements.loadDataBtn.addEventListener('click', () => this.loadSeatArrangement());
        }
        
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => this.refreshData());
        }
        
        // 교사/관리자 전용 기능
        if (this.options.isTeacher) {
            if (this.elements.selectionModeToggle) {
                this.elements.selectionModeToggle.addEventListener('change', (e) => {
                    this.toggleSelectionMode(e.target.checked);
                });
            }
            
            if (this.elements.markAbsentBtn) {
                this.elements.markAbsentBtn.addEventListener('click', () => this.markAttendance('absent'));
            }
            
            if (this.elements.markPresentBtn) {
                this.elements.markPresentBtn.addEventListener('click', () => this.markAttendance('present'));
            }
        }
        
        // 모달 이벤트
        if (this.elements.modal) {
            const closeBtn = this.elements.modal.querySelector('.close');
            const modalCloseBtn = document.getElementById('modal-close');
            
            if (closeBtn) closeBtn.addEventListener('click', () => this.closeModal());
            if (modalCloseBtn) modalCloseBtn.addEventListener('click', () => this.closeModal());
            
            this.elements.modal.addEventListener('click', (e) => {
                if (e.target === this.elements.modal) {
                    this.closeModal();
                }
            });
        }
        
        // 알림 이벤트
        if (this.elements.notification) {
            const closeBtn = this.elements.notification.querySelector('.notification-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.hideNotification());
            }
        }
        
        // 키보드 단축키
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    /**
     * 초기 데이터 로드
     */
    async loadInitialData() {
        this.updateCurrentDate();
        this.updateCurrentGrade();
        this.updateCurrentPeriod();
        
        // 초기 자리배치 데이터 로드
        await this.loadSeatArrangement();
    }
    
    /**
     * 현재 날짜 업데이트
     */
    updateCurrentDate() {
        this.currentDate = this.elements.datePicker?.value || new Date().toISOString().split('T')[0];
        console.log('Date updated:', this.currentDate);
    }
    
    /**
     * 현재 학년 업데이트
     */
    updateCurrentGrade() {
        this.currentGrade = parseInt(this.elements.gradeSelect?.value) || 1;
        this.updateClassroomTitle();
        console.log('Grade updated:', this.currentGrade);
    }
    
    /**
     * 현재 교시 업데이트
     */
    updateCurrentPeriod() {
        this.currentPeriod = parseInt(this.elements.periodSelect?.value) || 1;
        console.log('Period updated:', this.currentPeriod);
    }
    
    /**
     * 교실 제목 업데이트
     */
    updateClassroomTitle() {
        if (this.elements.classroomTitle) {
            this.elements.classroomTitle.textContent = `${this.currentGrade}학년 자율학습실`;
        }
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
            this.seatData = data;
            this.renderSeatGrid(data);
            
            console.log('Seat arrangement loaded:', data);
            
        } catch (error) {
            console.error('Failed to load seat arrangement:', error);
            this.showNotification('자리배치 데이터 로드에 실패했습니다: ' + error.message, 'error');
            this.showErrorGrid();
        }
    }
    
    /**
     * 데이터 새로고침
     */
    async refreshData() {
        this.selectedStudents.clear();
        this.updateSelectionDisplay();
        await this.loadSeatArrangement();
        this.showNotification('데이터를 새로고침했습니다.', 'success');
    }
    
    /**
     * 로딩 표시
     */
    showLoading() {
        if (this.elements.seatGrid) {
            this.elements.seatGrid.innerHTML = '<div class="loading">자리배치 데이터를 불러오는 중...</div>';
        }
    }
    
    /**
     * 오류 그리드 표시
     */
    showErrorGrid() {
        if (this.elements.seatGrid) {
            this.elements.seatGrid.innerHTML = `
                <div class="loading" style="color: #e53e3e;">
                    데이터를 불러올 수 없습니다.<br>
                    <button onclick="window.seatingManager.loadSeatArrangement()" class="btn btn-primary" style="margin-top: 12px;">
                        다시 시도
                    </button>
                </div>
            `;
        }
    }
    
    /**
     * 자리배치 그리드 렌더링
     */
    renderSeatGrid(data) {
        if (!this.elements.seatGrid || !data) return;
        
        this.elements.seatGrid.innerHTML = '';
        
        if (!data.sections || data.sections.length === 0) {
            this.elements.seatGrid.innerHTML = '<div class="loading">자리배치 데이터가 없습니다.</div>';
            return;
        }
        
        // 섹션별로 렌더링
        data.sections.forEach(section => {
            const sectionEl = this.createSectionElement(section);
            this.elements.seatGrid.appendChild(sectionEl);
        });
        
        console.log('Seat grid rendered with', data.sections.length, 'sections');
    }
    
    /**
     * 섹션 요소 생성
     */
    createSectionElement(section) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'seat-section';
        
        // 섹션 제목
        const title = document.createElement('div');
        title.className = 'section-title';
        title.textContent = section.name || 'Unknown Section';
        sectionDiv.appendChild(title);
        
        // 좌석 행들
        if (section.rows && section.rows.length > 0) {
            section.rows.forEach(row => {
                const rowDiv = document.createElement('div');
                rowDiv.className = 'section-row';
                
                row.seats.forEach(seat => {
                    const seatEl = this.createSeatElement(seat);
                    rowDiv.appendChild(seatEl);
                });
                
                sectionDiv.appendChild(rowDiv);
            });
        }
        
        return sectionDiv;
    }
    
    /**
     * 좌석 요소 생성
     */
    createSeatElement(seat) {
        const seatDiv = document.createElement('div');
        seatDiv.className = 'seat-item';
        
        if (!seat.student) {
            // 빈 좌석
            seatDiv.classList.add('empty');
            seatDiv.innerHTML = '<div class="seat-number">빈자리</div>';
            return seatDiv;
        }
        
        // 학생이 배정된 좌석
        const student = seat.student;
        seatDiv.classList.add('occupied');
        seatDiv.dataset.studentId = student.id;
        seatDiv.dataset.seatPosition = seat.position;
        
        // 출석 상태에 따른 클래스 추가
        if (seat.attendance_status) {
            seatDiv.classList.add(seat.attendance_status);
        } else {
            seatDiv.classList.add('present'); // 기본값
        }
        
        // HTML 구성
        seatDiv.innerHTML = `
            <div class="seat-number">${student.student_number || ''}</div>
            <div class="seat-name">${student.name || 'Unknown'}</div>
            ${seat.activity ? `<div class="seat-activity">${seat.activity}</div>` : ''}
            <div class="seat-status-indicator ${seat.attendance_status || 'present'}"></div>
        `;
        
        // 클릭 이벤트 리스너
        seatDiv.addEventListener('click', () => this.handleSeatClick(seat));
        
        return seatDiv;
    }
    
    /**
     * 좌석 클릭 처리
     */
    handleSeatClick(seat) {
        if (!seat.student) return;
        
        if (this.selectionMode && this.options.isTeacher) {
            // 선택 모드에서는 다중 선택
            this.toggleStudentSelection(seat.student.id);
        } else {
            // 일반 모드에서는 학생 정보 모달 표시
            this.showStudentModal(seat.student, seat);
        }
    }
    
    /**
     * 학생 선택/해제 토글
     */
    toggleStudentSelection(studentId) {
        if (this.selectedStudents.has(studentId)) {
            this.selectedStudents.delete(studentId);
        } else {
            this.selectedStudents.add(studentId);
        }
        
        this.updateSelectionDisplay();
    }
    
    /**
     * 선택 표시 업데이트
     */
    updateSelectionDisplay() {
        // 모든 좌석의 선택 상태 업데이트
        document.querySelectorAll('.seat-item[data-student-id]').forEach(seatEl => {
            const studentId = seatEl.dataset.studentId;
            if (this.selectedStudents.has(studentId)) {
                seatEl.classList.add('selected');
            } else {
                seatEl.classList.remove('selected');
            }
        });
        
        // 선택된 학생 수 표시
        if (this.elements.selectedCount) {
            this.elements.selectedCount.textContent = `선택된 학생: ${this.selectedStudents.size}명`;
        }
        
        // 버튼 활성화/비활성화
        const hasSelection = this.selectedStudents.size > 0;
        if (this.elements.markAbsentBtn) {
            this.elements.markAbsentBtn.disabled = !hasSelection;
        }
        if (this.elements.markPresentBtn) {
            this.elements.markPresentBtn.disabled = !hasSelection;
        }
    }
    
    /**
     * 선택 모드 토글
     */
    toggleSelectionMode(enabled) {
        this.selectionMode = enabled;
        
        if (!enabled) {
            this.selectedStudents.clear();
            this.updateSelectionDisplay();
        }
        
        // UI 업데이트
        document.body.classList.toggle('selection-mode', enabled);
        
        console.log('Selection mode:', enabled);
    }
    
    /**
     * 출석/부재 처리
     */
    async markAttendance(status) {
        if (this.selectedStudents.size === 0) {
            this.showNotification('학생을 선택해주세요.', 'error');
            return;
        }
        
        const studentIds = Array.from(this.selectedStudents);
        
        try {
            const response = await fetch('/seating/api/mark-attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: this.currentDate,
                    period: this.currentPeriod,
                    student_ids: studentIds,
                    status: status,
                    teacher_id: this.options.userId
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Network error');
            }
            
            const result = await response.json();
            
            // 성공 처리
            this.selectedStudents.clear();
            this.updateSelectionDisplay();
            
            // 자리배치 다시 로드
            await this.loadSeatArrangement();
            
            // 최근 변경사항 업데이트
            this.updateRecentChanges(result.changes);
            
            const statusText = status === 'absent' ? '부재' : '복귀';
            this.showNotification(`${studentIds.length}명의 학생을 ${statusText} 처리했습니다.`, 'success');
            
        } catch (error) {
            console.error('Failed to mark attendance:', error);
            this.showNotification('출석 처리에 실패했습니다: ' + error.message, 'error');
        }
    }
    
    /**
     * 최근 변경사항 업데이트
     */
    updateRecentChanges(changes) {
        if (!this.elements.recentChanges || !changes) return;
        
        const changesHtml = changes.map(change => `
            <div class="change-item">
                <div class="change-info">
                    ${change.student_name}: ${change.status === 'absent' ? '부재' : '복귀'}
                </div>
                <div class="change-time">${new Date(change.timestamp).toLocaleTimeString()}</div>
            </div>
        `).join('');
        
        this.elements.recentChanges.innerHTML = changesHtml || '<div class="change-item">최근 변경사항이 없습니다.</div>';
    }
    
    /**
     * 학생 정보 모달 표시
     */
    showStudentModal(student, seat) {
        if (!this.elements.modal) return;
        
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        
        if (modalTitle) modalTitle.textContent = `${student.name} 학생 정보`;
        
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="student-info">
                    <p><strong>학번:</strong> ${student.student_number || 'N/A'}</p>
                    <p><strong>이름:</strong> ${student.name}</p>
                    <p><strong>좌석 위치:</strong> ${seat.position || 'N/A'}</p>
                    <p><strong>출석 상태:</strong> 
                        <span class="status-badge ${seat.attendance_status || 'present'}">
                            ${this.getStatusText(seat.attendance_status)}
                        </span>
                    </p>
                    ${seat.activity ? `<p><strong>현재 활동:</strong> ${seat.activity}</p>` : ''}
                </div>
            `;
        }
        
        this.elements.modal.style.display = 'block';
    }
    
    /**
     * 상태 텍스트 반환
     */
    getStatusText(status) {
        switch (status) {
            case 'present': return '출석';
            case 'absent': return '부재';
            case 'activity': return '활동 중';
            default: return '출석';
        }
    }
    
    /**
     * 모달 닫기
     */
    closeModal() {
        if (this.elements.modal) {
            this.elements.modal.style.display = 'none';
        }
    }
    
    /**
     * 알림 표시
     */
    showNotification(message, type = 'info') {
        if (!this.elements.notification) return;
        
        const messageEl = document.getElementById('notification-message');
        if (messageEl) messageEl.textContent = message;
        
        this.elements.notification.className = `notification ${type} show`;
        
        // 3초 후 자동 숨김
        setTimeout(() => this.hideNotification(), 3000);
    }
    
    /**
     * 알림 숨김
     */
    hideNotification() {
        if (this.elements.notification) {
            this.elements.notification.classList.remove('show');
        }
    }
    
    /**
     * 키보드 단축키 처리
     */
    handleKeyboard(e) {
        if (e.ctrlKey) {
            switch (e.key) {
                case 'r':
                    e.preventDefault();
                    this.refreshData();
                    break;
                case 's':
                    if (this.options.isTeacher) {
                        e.preventDefault();
                        if (this.elements.selectionModeToggle) {
                            this.elements.selectionModeToggle.click();
                        }
                    }
                    break;
            }
        }
        
        if (e.key === 'Escape') {
            this.closeModal();
            if (this.selectionMode) {
                this.selectedStudents.clear();
                this.updateSelectionDisplay();
            }
        }
    }
}

// 유틸리티 함수들
window.SeatingUtils = {
    /**
     * 날짜 포맷팅
     */
    formatDate(date) {
        return new Date(date).toLocaleDateString('ko-KR');
    },
    
    /**
     * 시간 포맷팅
     */
    formatTime(date) {
        return new Date(date).toLocaleTimeString('ko-KR');
    },
    
    /**
     * 교시 텍스트 반환
     */
    getPeriodText(period) {
        if (period >= 1 && period <= 7) {
            return `${period}교시`;
        } else if (period >= 11 && period <= 15) {
            return `자습${period - 10}`;
        } else {
            return `${period}교시`;
        }
    }
};