(function() {
    document.querySelectorAll('.pdf-file-input').forEach(function(input) {
        input.addEventListener('change', function() {
            var file = this.files[0];
            if (!file) return;

            if (file.type !== 'application/pdf') {
                alert('Only PDF files are allowed.');
                this.value = '';
                return;
            }

            var container = this.closest('.pdf-upload-widget');
            var progress = container.querySelector('.pdf-upload-progress');
            var progressBar = progress.querySelector('progress');
            var statusEl = progress.querySelector('.pdf-upload-status');
            var hiddenInput = container.querySelector('input[type="hidden"]');
            var uploadUrl = this.getAttribute('data-upload-url');

            progress.style.display = '';
            statusEl.textContent = 'Requesting upload URL...';

            var formData = new FormData();
            formData.append('filename', file.name);

            fetch(uploadUrl, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) {
                    statusEl.textContent = 'Error: ' + data.error;
                    return;
                }

                statusEl.textContent = 'Uploading to Backblaze...';

                var uploadForm = new FormData();
                Object.keys(data.fields).forEach(function(k) {
                    uploadForm.append(k, data.fields[k]);
                });
                uploadForm.append('file', file);

                var xhr = new XMLHttpRequest();
                xhr.open('POST', data.url, true);

                xhr.upload.onprogress = function(e) {
                    if (e.lengthComputable) {
                        var pct = Math.round(e.loaded / e.total * 100);
                        progressBar.value = pct;
                    }
                };

                xhr.onload = function() {
                    if (xhr.status === 204) {
                        statusEl.textContent = 'Upload complete!';
                        progressBar.value = 100;
                        hiddenInput.value = data.key;
                    } else {
                        statusEl.textContent = 'Upload failed (HTTP ' + xhr.status + ')';
                    }
                };

                xhr.onerror = function() {
                    statusEl.textContent = 'Upload failed — network error';
                };

                xhr.send(uploadForm);
            })
            .catch(function(err) {
                statusEl.textContent = 'Error: ' + err.message;
            });
        });
    });
})();
