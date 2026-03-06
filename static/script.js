document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refresh-btn');
    
    refreshBtn.addEventListener('click', function() {
        refreshBtn.textContent = '⏳ Refreshing...';
        refreshBtn.disabled = true;
        
        fetch('/api/refresh')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Reload page to show fresh data
                    window.location.reload();
                } else {
                    alert('Refresh failed - using cached data');
                    refreshBtn.textContent = '↻ Refresh Inventory';
                    refreshBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Connection error - please try again');
                refreshBtn.textContent = '↻ Refresh Inventory';
                refreshBtn.disabled = false;
            });
    });
    
    // Add click handlers for action buttons
    document.querySelectorAll('.btn-primary').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.laptop-card');
            const title = card.querySelector('.laptop-title').textContent;
            alert(`In production: "${title}" would be added directly to your Squarespace store with all details and pricing.`);
        });
    });
    
    document.querySelectorAll('.btn-secondary').forEach(button => {
        button.addEventListener('click', function() {
            alert('This would open the original eBay listing for reference. In production, this helps you verify vendor details.');
        });
    });
});