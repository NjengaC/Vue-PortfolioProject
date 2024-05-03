<<<<<<< HEAD
function toggleRiderStatus(riderId) {
	fetch(`/toggle_rider_status/${riderId}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		}
	})
		.then(response => response.json())
		.then(data => {
			// Update the UI or perform any other action based on the returned status
			console.log('Rider status updated:', data.status);
		})
		.catch(error => {
			console.error('Error toggling rider status:', error);
		});
=======
// Get the toggle switch element
var toggle = document.getElementById('toggle');

// Add an event listener to listen for changes in the toggle switch
toggle.addEventListener('change', function() {
  // Call the updateRiderStatus function when the toggle switch is changed
  updateRiderStatus();
});

// Define the updateRiderStatus function
function updateRiderStatus() {
  var rider_id = toggle.getAttribute('data-rider-id');
  var status = toggle.checked ? 'available' : 'unavailable';

  var data = {
    rider_id: rider_id,
    status: status
  };

  fetch('/update_rider_status', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    console.log(data);
    // Handle success response here
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
    // Handle error here
  });
>>>>>>> 319c29311d7d4b5ce8883d48b4b471cf62e2e189
}
