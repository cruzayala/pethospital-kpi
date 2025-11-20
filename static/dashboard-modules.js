// dashboard-modules.js
// Interactive Dashboard Modules with Plotly.js

// ============================================================================
// OVERVIEW MODULE
// ============================================================================
async function loadOverview() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/summary?days=${currentPeriod}`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Metrics Cards
        html += '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">';

        const centers = data.centers;
        const totalOrders = centers.centers.reduce((sum, c) => sum + c.metrics.total_orders, 0);
        const totalResults = centers.centers.reduce((sum, c) => sum + c.metrics.total_results, 0);
        const totalPets = centers.centers.reduce((sum, c) => sum + c.metrics.total_pets, 0);
        const totalOwners = 0; // Not available in API response

        html += createMetricCard('Órdenes Totales', totalOrders, 'fas fa-file-medical');
        html += createMetricCard('Resultados', totalResults, 'fas fa-flask');
        html += createMetricCard('Mascotas', totalPets, 'fas fa-paw');
        html += createMetricCard('Propietarios', totalOwners, 'fas fa-users');

        html += '</div>';

        // Charts Row
        html += '<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">';

        // Top Centers Chart
        html += '<div class="chart-container"><div id="chart-top-centers"></div></div>';

        // Species Distribution
        html += '<div class="chart-container"><div id="chart-species"></div></div>';

        html += '</div>';

        // Top Tests Table
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Top 10 Pruebas Más Solicitadas</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Prueba</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Centros</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Crecimiento</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        data.top_tests.tests.slice(0, 10).forEach((test, index) => {
            html += '<tr>';
            html += `<td class="px-6 py-4 whitespace-nowrap"><span class="font-medium">#${index + 1}</span> ${test.test_code}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(test.total_count)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${test.centers_count} centros</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${getGrowthBadge(test.growth_rate)}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';

        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Top Centers Chart
        const topCenters = centers.centers.slice(0, 10);
        Plotly.newPlot('chart-top-centers', [{
            type: 'bar',
            x: topCenters.map(c => c.center_name),
            y: topCenters.map(c => c.metrics.total_orders),
            text: topCenters.map(c => formatNumber(c.metrics.total_orders)),
            textposition: 'auto',
            marker: {
                color: '#3b82f6',
                line: { color: '#2563eb', width: 1 }
            },
            hovertemplate: '<b>%{x}</b><br>Órdenes: %{y}<extra></extra>'
        }], getPlotlyLayout('Top 10 Centros por Órdenes'), {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        });

        // Render Species Distribution
        const species = data.species.species;
        Plotly.newPlot('chart-species', [{
            type: 'pie',
            labels: species.map(s => s.name),
            values: species.map(s => s.total_count),
            textinfo: 'label+percent',
            hovertemplate: '<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
            marker: {
                colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }
        }], getPlotlyLayout('Distribución de Especies'), {
            responsive: true
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading overview:', error);
        showError('Error al cargar el resumen general');
    }
}

function createMetricCard(title, value, icon) {
    return `
        <div class="metric-card p-6 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600 dark:text-gray-400">${title}</p>
                    <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">${formatNumber(value)}</p>
                </div>
                <div class="text-3xl text-blue-500">
                    <i class="${icon}"></i>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// CENTERS COMPARISON MODULE
// ============================================================================
async function loadCentersComparison() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/centers/comparison?days=${currentPeriod}`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Summary Stats
        html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
        html += createMetricCard('Total Centros', data.total_centers, 'fas fa-hospital');
        html += createMetricCard('Órdenes Totales', data.aggregates.total_orders, 'fas fa-file-medical');
        html += createMetricCard('Resultados Totales', data.aggregates.total_results, 'fas fa-flask');
        html += '</div>';

        // Bar Chart
        html += '<div class="chart-container"><div id="chart-centers-bars"></div></div>';

        // Rankings Table
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Ranking de Centros</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Rank</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Centro</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Órdenes</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Resultados</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Mascotas</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Crecimiento</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Nivel</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        data.centers.forEach((center, index) => {
            const levelBadge = getActivityLevelBadge('medium'); // activity_level not in API
            html += '<tr class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer" onclick="loadCenterDetails(\'' + center.center_code + '\')">';
            html += `<td class="px-6 py-4 whitespace-nowrap"><span class="font-bold text-lg">#${center.rank}</span></td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap font-medium">${center.center_name}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(center.metrics.total_orders)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(center.metrics.total_results)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(center.metrics.total_pets)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${getGrowthBadge(center.growth_rate_percent)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${levelBadge}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';
        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Bar Chart
        Plotly.newPlot('chart-centers-bars', [{
            type: 'bar',
            x: data.centers.map(c => c.center_name),
            y: data.centers.map(c => c.metrics.total_orders),
            name: 'Órdenes',
            marker: { color: '#3b82f6' },
            text: data.centers.map(c => formatNumber(c.metrics.total_orders)),
            textposition: 'auto'
        }, {
            type: 'bar',
            x: data.centers.map(c => c.center_name),
            y: data.centers.map(c => c.metrics.total_results),
            name: 'Resultados',
            marker: { color: '#10b981' },
            text: data.centers.map(c => formatNumber(c.metrics.total_results)),
            textposition: 'auto'
        }], getPlotlyLayout('Comparación de Centros'), {
            responsive: true,
            displayModeBar: true
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading centers comparison:', error);
        showError('Error al cargar comparación de centros');
    }
}

function getActivityLevelBadge(level) {
    const badges = {
        'high': '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Alto</span>',
        'medium': '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Medio</span>',
        'low': '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Bajo</span>'
    };
    return badges[level] || badges['low'];
}

// ============================================================================
// CENTER DETAILS MODULE
// ============================================================================
async function loadCenterDetails(centerCode) {
    showLoading();
    currentModule = 'center-details';
    document.getElementById('module-title').textContent = `Detalle: ${centerCode}`;

    try {
        const summaryResponse = await axios.get(`/analytics/centers/summary/${centerCode}?days=${currentPeriod}`);
        const trendsResponse = await axios.get(`/analytics/centers/trends/${centerCode}?days=${currentPeriod}`);

        const summary = summaryResponse.data;
        const trends = trendsResponse.data;

        let html = '<div class="space-y-6">';

        // Back button and Header
        html += '<div class="flex items-center justify-between mb-4">';
        html += '<button onclick="loadCentersComparison()" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">';
        html += '<i class="fas fa-arrow-left mr-2"></i>Volver a Comparación';
        html += '</button>';
        html += `<div class="text-right">`;
        html += `<h2 class="text-2xl font-bold text-gray-900 dark:text-white">${summary.center_name}</h2>`;
        html += `<p class="text-sm text-gray-500 dark:text-gray-400">Código: ${centerCode}</p>`;
        html += `</div>`;
        html += '</div>';

        // Main Metrics Cards
        html += '<div class="grid grid-cols-1 md:grid-cols-4 gap-4">';
        html += createMetricCard('Órdenes', summary.metrics.total_orders, 'fas fa-file-medical');
        html += createMetricCard('Resultados', summary.metrics.total_results, 'fas fa-flask');
        html += createMetricCard('Mascotas', summary.metrics.unique_pets, 'fas fa-paw');
        html += createMetricCard('Propietarios', summary.metrics.unique_owners, 'fas fa-users');
        html += '</div>';

        // Performance Indicators
        if (summary.performance) {
            html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
            html += '<div class="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">';
            html += '<div class="flex items-center justify-between">';
            html += '<div>';
            html += '<p class="text-sm font-medium text-blue-600 dark:text-blue-400">Promedio Órdenes/Día</p>';
            html += `<p class="text-2xl font-bold text-blue-900 dark:text-blue-100">${(summary.metrics.total_orders / currentPeriod).toFixed(1)}</p>`;
            html += '</div>';
            html += '<i class="fas fa-chart-line text-3xl text-blue-400"></i>';
            html += '</div>';
            html += '</div>';

            html += '<div class="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">';
            html += '<div class="flex items-center justify-between">';
            html += '<div>';
            html += '<p class="text-sm font-medium text-green-600 dark:text-green-400">Tasa de Resultados</p>';
            const resultRate = summary.metrics.total_orders > 0 ? (summary.metrics.total_results / summary.metrics.total_orders * 100).toFixed(1) : 0;
            html += `<p class="text-2xl font-bold text-green-900 dark:text-green-100">${resultRate}%</p>`;
            html += '</div>';
            html += '<i class="fas fa-check-circle text-3xl text-green-400"></i>';
            html += '</div>';
            html += '</div>';

            html += '<div class="p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">';
            html += '<div class="flex items-center justify-between">';
            html += '<div>';
            html += '<p class="text-sm font-medium text-purple-600 dark:text-purple-400">Pruebas Únicas</p>';
            html += `<p class="text-2xl font-bold text-purple-900 dark:text-purple-100">${summary.top_tests.length}</p>`;
            html += '</div>';
            html += '<i class="fas fa-vial text-3xl text-purple-400"></i>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }

        // Trends Chart with Period Info
        html += '<div class="chart-container">';
        html += `<h3 class="text-lg font-semibold mb-2">Tendencia Diaria (últimos ${currentPeriod} días)</h3>`;
        html += '<div id="chart-trends"></div>';
        html += '</div>';

        // Two Column Layout for Charts
        html += '<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">';

        // Top Tests Chart
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Top 10 Pruebas Más Solicitadas</h3>';
        html += '<div id="chart-top-tests"></div>';
        html += '</div>';

        // Species Distribution Chart
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Distribución de Especies</h3>';
        html += '<div id="chart-center-species"></div>';
        html += '</div>';

        html += '</div>';

        // Module Usage (if available)
        if (summary.module_usage && summary.module_usage.length > 0) {
            html += '<div class="chart-container">';
            html += '<h3 class="text-lg font-semibold mb-4">Uso de Módulos del Sistema</h3>';
            html += '<div id="chart-modules"></div>';
            html += '</div>';
        }

        // Daily History Table
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Historial de Últimos 10 Días</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Fecha</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Órdenes</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Resultados</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Mascotas</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Propietarios</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        // Show last 10 days
        trends.daily_metrics.slice(-10).reverse().forEach(day => {
            html += '<tr>';
            html += `<td class="px-6 py-4 whitespace-nowrap font-medium">${day.date}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(day.orders)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(day.results)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(day.pets)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(day.owners)}</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';

        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Trends Chart
        const dates = trends.daily_metrics.map(d => d.date);
        Plotly.newPlot('chart-trends', [
            {
                type: 'scatter',
                mode: 'lines+markers',
                x: dates,
                y: trends.daily_metrics.map(d => d.orders),
                name: 'Órdenes',
                line: { color: '#3b82f6', width: 2 },
                marker: { size: 6 },
                hovertemplate: '<b>%{x}</b><br>Órdenes: %{y}<extra></extra>'
            },
            {
                type: 'scatter',
                mode: 'lines+markers',
                x: dates,
                y: trends.daily_metrics.map(d => d.results),
                name: 'Resultados',
                line: { color: '#10b981', width: 2 },
                marker: { size: 6 },
                hovertemplate: '<b>%{x}</b><br>Resultados: %{y}<extra></extra>'
            },
            {
                type: 'scatter',
                mode: 'lines+markers',
                x: dates,
                y: trends.daily_metrics.map(d => d.pets),
                name: 'Mascotas',
                line: { color: '#f59e0b', width: 2, dash: 'dot' },
                marker: { size: 4 },
                hovertemplate: '<b>%{x}</b><br>Mascotas: %{y}<extra></extra>'
            }
        ], getPlotlyLayout(''), {
            responsive: true,
            displayModeBar: true
        });

        // Render Top Tests Chart
        const topTests = summary.top_tests.slice(0, 10);
        Plotly.newPlot('chart-top-tests', [{
            type: 'bar',
            x: topTests.map(t => t.count),
            y: topTests.map(t => t.test_code),
            orientation: 'h',
            marker: {
                color: topTests.map((_, i) => `hsl(${220 - i * 15}, 70%, 50%)`)
            },
            text: topTests.map(t => formatNumber(t.count)),
            textposition: 'auto',
            hovertemplate: '<b>%{y}</b><br>Cantidad: %{x}<extra></extra>'
        }], getPlotlyLayout(''), {
            responsive: true,
            height: 400
        });

        // Render Species Distribution
        Plotly.newPlot('chart-center-species', [{
            type: 'pie',
            labels: summary.species_distribution.map(s => s.species || 'Desconocido'),
            values: summary.species_distribution.map(s => s.count),
            textinfo: 'label+percent',
            hovertemplate: '<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
            marker: {
                colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }
        }], getPlotlyLayout(''), {
            responsive: true,
            height: 400
        });

        // Render Module Usage if available
        if (summary.module_usage && summary.module_usage.length > 0) {
            Plotly.newPlot('chart-modules', [{
                type: 'bar',
                x: summary.module_usage.map(m => m.module_name),
                y: summary.module_usage.map(m => m.usage_count),
                marker: { color: '#8b5cf6' },
                text: summary.module_usage.map(m => formatNumber(m.usage_count)),
                textposition: 'auto'
            }], getPlotlyLayout(''), {
                responsive: true
            });
        }

        hideLoading();

    } catch (error) {
        console.error('Error loading center details:', error);
        showError('Error al cargar detalles del centro');
    }
}

// ============================================================================
// TOP TESTS MODULE
// ============================================================================
async function loadTopTests() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/tests/top-global?days=${currentPeriod}&limit=20`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Summary
        html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
        html += createMetricCard('Total Pruebas', data.total_tests, 'fas fa-vial');
        html += createMetricCard('Tipos Únicos', data.tests.length, 'fas fa-list');
        html += createMetricCard('Centros Activos', 'N/A', 'fas fa-hospital');
        html += '</div>';

        // Top Tests Bar Chart
        html += '<div class="chart-container"><div id="chart-tests-bar"></div></div>';

        // Tests Table with Details
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Top 20 Pruebas Más Solicitadas</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Rank</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Código</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Centros</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Crecimiento</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Popularidad</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        data.tests.forEach((test, index) => {
            const percentage = (test.total_count / data.total_tests * 100).toFixed(2);
            html += '<tr class="hover:bg-gray-50 dark:hover:bg-gray-800">';
            html += `<td class="px-6 py-4 whitespace-nowrap"><span class="font-bold">#${index + 1}</span></td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap font-medium">${test.code} - ${test.name}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(test.total_count)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${test.num_centers} centros</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${getGrowthBadge(test.growth_rate_percent)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${percentage}%</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';
        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Bar Chart (Top 15 for visibility)
        const top15 = data.tests.slice(0, 15);
        Plotly.newPlot('chart-tests-bar', [{
            type: 'bar',
            x: top15.map(t => t.code),
            y: top15.map(t => t.total_count),
            text: top15.map(t => formatNumber(t.total_count)),
            textposition: 'auto',
            marker: {
                color: top15.map((_, i) => `hsl(${220 - i * 10}, 70%, 50%)`),
            },
            hovertemplate: '<b>%{x}</b><br>Total: %{y}<extra></extra>'
        }], getPlotlyLayout('Top 15 Pruebas'), {
            responsive: true,
            displayModeBar: true
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading top tests:', error);
        showError('Error al cargar pruebas más solicitadas');
    }
}

// ============================================================================
// TEST CATEGORIES MODULE
// ============================================================================
async function loadTestCategories() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/tests/categories?days=${currentPeriod}`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Categories Grid
        html += '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';

        Object.entries(data.categories).forEach(([category, info]) => {
            html += `
                <div class="p-6 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
                    <h3 class="text-lg font-semibold mb-2">${category}</h3>
                    <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">${formatNumber(info.count)}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">${info.tests.length} pruebas únicas</p>
                    <div class="mt-4 flex flex-wrap gap-1">
                        ${info.tests.slice(0, 10).map(t =>
                            `<span class="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">${t}</span>`
                        ).join('')}
                        ${info.tests.length > 10 ? '<span class="text-xs text-gray-500">+' + (info.tests.length - 10) + ' más</span>' : ''}
                    </div>
                </div>
            `;
        });

        html += '</div>';

        // Category Distribution Chart
        html += '<div class="chart-container"><div id="chart-categories"></div></div>';

        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Pie Chart
        const categories = Object.entries(data.categories);
        Plotly.newPlot('chart-categories', [{
            type: 'pie',
            labels: categories.map(([name]) => name),
            values: categories.map(([, info]) => info.count),
            textinfo: 'label+percent',
            hovertemplate: '<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
            marker: {
                colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']
            }
        }], getPlotlyLayout('Distribución por Categorías'), {
            responsive: true
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading test categories:', error);
        showError('Error al cargar categorías de pruebas');
    }
}

// ============================================================================
// SPECIES DISTRIBUTION MODULE
// ============================================================================
async function loadSpeciesDistribution() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/species/distribution?days=${currentPeriod}`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Summary Cards
        html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
        html += createMetricCard('Total Pacientes', data.summary.total_animals, 'fas fa-paw');
        html += createMetricCard('Especies Únicas', data.summary.num_species, 'fas fa-list');
        html += createMetricCard('Centros', 'N/A', 'fas fa-hospital');
        html += '</div>';

        // Charts Row
        html += '<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">';

        // Pie Chart
        html += '<div class="chart-container"><div id="chart-species-pie"></div></div>';

        // Bar Chart
        html += '<div class="chart-container"><div id="chart-species-bar"></div></div>';

        html += '</div>';

        // Species Details Table
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Distribución Detallada</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Especie</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Porcentaje</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Centros</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        data.species.forEach(species => {
            html += '<tr>';
            html += `<td class="px-6 py-4 whitespace-nowrap font-medium">${species.name || 'Desconocido'}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(species.total_count)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${species.percentage.toFixed(1)}%</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${species.num_centers} centros</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';
        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Pie Chart
        Plotly.newPlot('chart-species-pie', [{
            type: 'pie',
            labels: data.species.map(s => s.name || 'Desconocido'),
            values: data.species.map(s => s.total_count),
            textinfo: 'label+percent',
            hovertemplate: '<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
            marker: {
                colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }
        }], getPlotlyLayout('Distribución de Especies'), {
            responsive: true
        });

        // Render Bar Chart
        Plotly.newPlot('chart-species-bar', [{
            type: 'bar',
            x: data.species.map(s => s.name || 'Desconocido'),
            y: data.species.map(s => s.total_count),
            text: data.species.map(s => formatNumber(s.total_count)),
            textposition: 'auto',
            marker: { color: '#3b82f6' }
        }], getPlotlyLayout('Total por Especie'), {
            responsive: true
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading species distribution:', error);
        showError('Error al cargar distribución de especies');
    }
}

// ============================================================================
// TOP BREEDS MODULE
// ============================================================================
async function loadTopBreeds() {
    showLoading();

    try {
        const response = await axios.get(`/analytics/breeds/top?days=${currentPeriod}&limit=30`);
        const data = response.data;

        let html = '<div class="space-y-6">';

        // Summary
        html += '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">';
        html += createMetricCard('Total Razas', data.summary.total_different_breeds, 'fas fa-dog');
        html += createMetricCard('Mostrando Top', data.summary.showing_top, 'fas fa-paw');
        html += createMetricCard('Centros', 'N/A', 'fas fa-hospital');
        html += '</div>';

        // Top Breeds Chart
        html += '<div class="chart-container"><div id="chart-breeds"></div></div>';

        // Breeds Table
        html += '<div class="chart-container">';
        html += '<h3 class="text-lg font-semibold mb-4">Top 30 Razas Más Comunes</h3>';
        html += '<div class="overflow-x-auto">';
        html += '<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">';
        html += '<thead class="bg-gray-50 dark:bg-gray-800">';
        html += '<tr>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Rank</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Raza</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Especie</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total</th>';
        html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Porcentaje</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">';

        data.breeds.forEach((breed, index) => {
            html += '<tr>';
            html += `<td class="px-6 py-4 whitespace-nowrap"><span class="font-bold">#${index + 1}</span></td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap font-medium">${breed.breed || 'Desconocido'}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${breed.species || 'N/A'}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">${formatNumber(breed.total_count)}</td>`;
            html += `<td class="px-6 py-4 whitespace-nowrap">N/A</td>`;
            html += '</tr>';
        });

        html += '</tbody></table></div></div>';
        html += '</div>';

        document.getElementById('content').innerHTML = html;

        // Render Bar Chart (Top 15)
        const top15 = data.breeds.slice(0, 15);
        Plotly.newPlot('chart-breeds', [{
            type: 'bar',
            y: top15.map(b => b.breed || 'Desconocido'),
            x: top15.map(b => b.total_count),
            orientation: 'h',
            text: top15.map(b => formatNumber(b.total_count)),
            textposition: 'auto',
            marker: { color: '#10b981' },
            hovertemplate: '<b>%{y}</b><br>Total: %{x}<extra></extra>'
        }], getPlotlyLayout('Top 15 Razas'), {
            responsive: true,
            height: 500
        });

        hideLoading();

    } catch (error) {
        console.error('Error loading top breeds:', error);
        showError('Error al cargar razas más comunes');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
function showLoading() {
    document.getElementById('content').innerHTML = `
        <div class="flex items-center justify-center h-64">
            <div class="text-center">
                <i class="fas fa-spinner fa-spin text-4xl text-blue-500 mb-4"></i>
                <p class="text-gray-600 dark:text-gray-400">Cargando datos...</p>
            </div>
        </div>
    `;
}

function hideLoading() {
    // Content is already replaced by the module
}

function showError(message) {
    document.getElementById('content').innerHTML = `
        <div class="flex items-center justify-center h-64">
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                <p class="text-red-600 dark:text-red-400 font-semibold">${message}</p>
                <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    Reintentar
                </button>
            </div>
        </div>
    `;
}
