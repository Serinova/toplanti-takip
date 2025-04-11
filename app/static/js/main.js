/* Main JavaScript for Toplanti Takip Programi */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Sidebar toggle for mobile
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
        });
    }

    // Flash message auto-dismiss
    var flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            var closeButton = flash.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Confirm delete modals
    var confirmDeleteButtons = document.querySelectorAll('[data-confirm]');
    confirmDeleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Date picker initialization
    var datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(function(picker) {
            flatpickr(picker, {
                dateFormat: "d.m.Y",
                locale: "tr"
            });
        });
    }

    // Time picker initialization
    var timePickers = document.querySelectorAll('.timepicker');
    if (timePickers.length > 0) {
        timePickers.forEach(function(picker) {
            flatpickr(picker, {
                enableTime: true,
                noCalendar: true,
                dateFormat: "H:i",
                time_24hr: true,
                locale: "tr"
            });
        });
    }

    // DateTime picker initialization
    var dateTimePickers = document.querySelectorAll('.datetimepicker');
    if (dateTimePickers.length > 0) {
        dateTimePickers.forEach(function(picker) {
            flatpickr(picker, {
                enableTime: true,
                dateFormat: "d.m.Y H:i",
                time_24hr: true,
                locale: "tr"
            });
        });
    }

    // Select2 initialization
    var select2Elements = document.querySelectorAll('.select2');
    if (typeof $.fn.select2 !== 'undefined' && select2Elements.length > 0) {
        $(select2Elements).select2({
            theme: 'bootstrap-5',
            width: '100%'
        });
    }

    // CKEditor initialization
    var richTextEditors = document.querySelectorAll('.rich-text-editor');
    if (typeof ClassicEditor !== 'undefined' && richTextEditors.length > 0) {
        richTextEditors.forEach(function(editor) {
            ClassicEditor
                .create(editor, {
                    toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'undo', 'redo'],
                    language: 'tr'
                })
                .catch(function(error) {
                    console.error(error);
                });
        });
    }

    // Task status update
    var taskStatusSelects = document.querySelectorAll('.task-status-select');
    taskStatusSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Notification mark as read
    var notificationReadButtons = document.querySelectorAll('.notification-read-btn');
    notificationReadButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var notificationId = this.getAttribute('data-notification-id');
            
            fetch('/bildirim/okundu/' + notificationId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(function(response) {
                if (response.ok) {
                    var notificationItem = document.getElementById('notification-' + notificationId);
                    if (notificationItem) {
                        notificationItem.classList.remove('bg-light');
                        button.style.display = 'none';
                        
                        // Update notification counter
                        var counter = document.querySelector('.notification-counter');
                        if (counter) {
                            var count = parseInt(counter.textContent);
                            if (count > 0) {
                                count--;
                                counter.textContent = count;
                                if (count === 0) {
                                    counter.style.display = 'none';
                                }
                            }
                        }
                    }
                }
            })
            .catch(function(error) {
                console.error('Error marking notification as read:', error);
            });
        });
    });

    // Helper function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    // Meeting participant add
    var participantSelect = document.getElementById('participant-select');
    var participantList = document.getElementById('participant-list');
    
    if (participantSelect && participantList) {
        document.getElementById('add-participant-btn').addEventListener('click', function() {
            var option = participantSelect.options[participantSelect.selectedIndex];
            if (option && option.value) {
                var participantId = option.value;
                var participantName = option.text;
                
                // Check if already added
                if (!document.querySelector('input[name="participants[]"][value="' + participantId + '"]')) {
                    var listItem = document.createElement('li');
                    listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                    listItem.innerHTML = 
                        participantName + 
                        '<input type="hidden" name="participants[]" value="' + participantId + '">' +
                        '<button type="button" class="btn btn-sm btn-outline-danger remove-participant"><i class="fas fa-times"></i></button>';
                    
                    participantList.appendChild(listItem);
                    
                    // Add remove event listener
                    listItem.querySelector('.remove-participant').addEventListener('click', function() {
                        listItem.remove();
                    });
                }
            }
        });
    }

    // AI features
    var aiSummaryBtn = document.getElementById('ai-summary-btn');
    if (aiSummaryBtn) {
        aiSummaryBtn.addEventListener('click', function() {
            var meetingId = this.getAttribute('data-meeting-id');
            var summaryContainer = document.getElementById('ai-summary-container');
            
            if (meetingId && summaryContainer) {
                summaryContainer.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
                
                fetch('/ai/toplanti-ozeti/' + meetingId, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        summaryContainer.innerHTML = '<div class="alert alert-success">' + data.summary + '</div>';
                    } else {
                        summaryContainer.innerHTML = '<div class="alert alert-danger">Özet oluşturulurken bir hata oluştu.</div>';
                    }
                })
                .catch(function(error) {
                    console.error('Error generating summary:', error);
                    summaryContainer.innerHTML = '<div class="alert alert-danger">Özet oluşturulurken bir hata oluştu.</div>';
                });
            }
        });
    }

    // AI task extraction
    var aiTaskBtn = document.getElementById('ai-task-btn');
    if (aiTaskBtn) {
        aiTaskBtn.addEventListener('click', function() {
            var meetingId = this.getAttribute('data-meeting-id');
            var taskContainer = document.getElementById('ai-task-container');
            
            if (meetingId && taskContainer) {
                taskContainer.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
                
                fetch('/ai/gorev-cikar/' + meetingId, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success && data.tasks.length > 0) {
                        var tasksHtml = '<div class="list-group">';
                        data.tasks.forEach(function(task) {
                            tasksHtml += '<div class="list-group-item">';
                            tasksHtml += '<div class="d-flex justify-content-between align-items-center">';
                            tasksHtml += '<h6 class="mb-1">' + task.title + '</h6>';
                            tasksHtml += '<a href="/gorev/olustur?title=' + encodeURIComponent(task.title) + '&description=' + encodeURIComponent(task.description) + '&meeting_id=' + meetingId + '" class="btn btn-sm btn-primary">Görev Oluştur</a>';
                            tasksHtml += '</div>';
                            tasksHtml += '<p class="mb-1">' + task.description + '</p>';
                            tasksHtml += '</div>';
                        });
                        tasksHtml += '</div>';
                        taskContainer.innerHTML = tasksHtml;
                    } else {
                        taskContainer.innerHTML = '<div class="alert alert-info">Toplantı notlarından görev çıkarılamadı.</div>';
                    }
                })
                .catch(function(error) {
                    console.error('Error extracting tasks:', error);
                    taskContainer.innerHTML = '<div class="alert alert-danger">Görevler çıkarılırken bir hata oluştu.</div>';
                });
            }
        });
    }

    // Chart.js initialization for reports
    if (typeof Chart !== 'undefined') {
        // Set default options
        Chart.defaults.font.family = "'Nunito', 'Helvetica', 'Arial', sans-serif";
        Chart.defaults.color = '#6c757d';
        
        // Custom chart initialization will be handled in specific pages
    }
});
