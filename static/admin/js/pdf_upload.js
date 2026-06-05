(function() {
  var uploadInProgress = false;
  var uploadComplete = false;
  var pendingFormSubmit = false;
  var theForm = null;

  function findForm(el) {
    while (el && el.tagName !== 'FORM') el = el.parentElement;
    return el;
  }

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

      uploadInProgress = true;
      uploadComplete = false;
      progress.style.display = '';
      statusEl.textContent = 'Requesting upload URL...';

      var formData = new FormData();
      formData.append('filename', file.name);

      fetch(uploadUrl, { method: 'POST', body: formData, credentials: 'same-origin' })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.error) {
          statusEl.textContent = 'Error: ' + data.error;
          uploadInProgress = false;
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
            progressBar.value = Math.round(e.loaded / e.total * 100);
          }
        };

        xhr.onload = function() {
          uploadInProgress = false;
          if (xhr.status === 204) {
            statusEl.textContent = 'Upload complete!';
            progressBar.value = 100;
            hiddenInput.value = data.key;
            uploadComplete = true;
            if (pendingFormSubmit && theForm) {
              pendingFormSubmit = false;
              theForm.submit();
            }
          } else {
            statusEl.textContent = 'Upload failed (HTTP ' + xhr.status + ')';
          }
        };

        xhr.onerror = function() {
          uploadInProgress = false;
          statusEl.textContent = 'Upload failed — network error';
        };

        xhr.send(uploadForm);
      })
      .catch(function(err) {
        uploadInProgress = false;
        statusEl.textContent = 'Error: ' + err.message;
      });
    });
  });

  document.addEventListener('submit', function(e) {
    if (uploadInProgress) {
      e.preventDefault();
      theForm = e.target;
      pendingFormSubmit = true;
      var container = document.querySelector('.pdf-upload-widget');
      if (container) {
        var statusEl = container.querySelector('.pdf-upload-status');
        if (statusEl) statusEl.textContent = 'Waiting for upload to finish...';
      }
    }
  }, true);
})();
