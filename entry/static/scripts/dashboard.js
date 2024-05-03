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
}
