document.addEventListener('DOMContentLoaded', function() {
  var uploadInProgress = false;
  var pendingSubmit = false;
  var targetForm = null;

  document.querySelectorAll('.pdf-file-input').forEach(function(input) {
    input.addEventListener('change', function() {
      var file = this.files[0];
      if (!file) return;
      if (file.type !== 'application/pdf') {
        alert('Only PDF files are allowed.');
        this.value = '';
        return;
      }

      var w = this.closest('.pdf-upload-widget');
      var progress = w.querySelector('.pdf-upload-progress');
      var bar = progress.querySelector('progress');
      var status = progress.querySelector('.pdf-upload-status');
      var hidden = w.querySelector('input[type="hidden"]');
      var uploadUrl = this.getAttribute('data-upload-url');

      uploadInProgress = true;
      progress.style.display = '';
      status.textContent = 'Getting upload URL...';

      var fd = new FormData();
      fd.append('filename', file.name);

      fetch(uploadUrl, { method: 'POST', body: fd, credentials: 'same-origin' })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        if (d.error) { status.textContent = 'Error: ' + d.error; uploadInProgress = false; return; }

        status.textContent = 'Uploading to Backblaze...';

        var xhr = new XMLHttpRequest();
        xhr.open('PUT', d.url, true);
        xhr.setRequestHeader('Content-Type', 'application/pdf');

        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) bar.value = Math.round(e.loaded / e.total * 100);
        };

        xhr.onload = function() {
          uploadInProgress = false;
          if (xhr.status >= 200 && xhr.status < 300) {
            status.textContent = 'Upload complete!';
            bar.value = 100;
            hidden.value = d.key;
            if (pendingSubmit && targetForm) {
              pendingSubmit = false;
              targetForm.submit();
            }
          } else {
            status.textContent = 'Upload failed (HTTP ' + xhr.status + ')';
          }
        };

        xhr.onerror = function() { uploadInProgress = false; status.textContent = 'Upload failed - network error'; };
        xhr.send(file);
      })
      .catch(function(err) { uploadInProgress = false; status.textContent = 'Error: ' + err.message; });
    });
  });

  document.addEventListener('submit', function(e) {
    if (uploadInProgress) {
      e.preventDefault();
      targetForm = e.target;
      pendingSubmit = true;
      var el = document.querySelector('.pdf-upload-status');
      if (el) el.textContent = 'Waiting for upload to finish before saving...';
    }
  }, true);
});
