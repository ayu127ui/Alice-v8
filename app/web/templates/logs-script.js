function loadBase64Image(eventId) {
  // Fallback to base64 if regular image load fails
  fetch(`/screenshot-base64/${eventId}`)
    .then(r => r.json())
    .then(d => {
      if (d.image) {
        const img = document.getElementById(`img-${eventId}`);
        img.src = d.image;
        img.style.display = 'block';
      } else {
        showPlaceholder(eventId);
      }
    })
    .catch(e => {
      console.log(`Failed to load base64 image: ${e}`);
      showPlaceholder(eventId);
    });
}

function showPlaceholder(eventId) {
  const img = document.getElementById(`img-${eventId}`);
  const placeholder = document.getElementById(`placeholder-${eventId}`);
  img.style.display = 'none';
  placeholder.style.display = 'flex';
}

function sendAlert(eventId, labels, score) {
  const button = event.target;
  button.disabled = true;
  button.textContent = '⏳ Sending...';

  fetch('/send-alert', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({event_id: eventId, labels: labels, score: score})
  })
  .then(r => r.json())
  .then(d => {
    showSuccessModal();
    button.disabled = false;
    button.textContent = '✉️ Send Alert';
  })
  .catch(e => {
    alert('Error sending alert: ' + e);
    button.disabled = false;
    button.textContent = '✉️ Send Alert';
  });
}

function showSuccessModal() {
  const modal = document.getElementById('successModal');
  modal.classList.add('show');
  
  // Auto-close after 3 seconds
  setTimeout(() => {
    modal.classList.remove('show');
  }, 3000);
}

function closeModal() {
  document.getElementById('successModal').classList.remove('show');
}

function showImageModal(src) {
  const modal = document.getElementById('imageModal');
  const img = document.getElementById('modalImage');
  img.src = src;
  modal.classList.add('show');
}

function closeImageModal() {
  document.getElementById('imageModal').classList.remove('show');
}

// Close modal when clicking outside
window.onclick = function(event) {
  const successModal = document.getElementById('successModal');
  const imageModal = document.getElementById('imageModal');
  if (event.target === successModal) {
    successModal.classList.remove('show');
  }
  if (event.target === imageModal) {
    imageModal.classList.remove('show');
  }
}
