function renderForecastChart(labels, temps, feels, humid) {
  const ctx = document.getElementById('tempChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: temps,
          borderColor: 'rgba(54,162,235,1)',
          backgroundColor: 'rgba(54,162,235,0.15)',
          tension: 0.25,
          yAxisID: 'y'
        },
        {
          label: 'Feels Like (°C)',
          data: feels,
          borderColor: 'rgba(255,99,132,1)',
          backgroundColor: 'rgba(255,99,132,0.12)',
          tension: 0.25,
          yAxisID: 'y'
        },
        {
          label: 'Humidity (%)',
          data: humid,
          borderColor: 'rgba(75,192,192,1)',
          backgroundColor: 'rgba(75,192,192,0.08)',
          type: 'bar',
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      stacked: false,
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: { display: true, text: 'Temperature (°C)' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Humidity (%)' }
        },
        x: {
          ticks: {
            callback: (val, index) => index % 4 === 0 ? labels[index] : ''
          }
        }
      },
      plugins: {
        legend: { position: 'top' }
      }
    }
  });
}