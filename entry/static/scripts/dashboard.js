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
}
