// Select relevant DOM elements
const addRecordBtn = document.getElementById('add-record-btn');
const viewDraftsBtn = document.getElementById('view-drafts-btn');
const viewHistoryBtn = document.getElementById('view-history-btn');
const recordEntries = document.getElementById('record-entries');

// Sample record data
let records = [
    { date: '2025-02-19', type: 'Blood Test', provider: 'Dr. Smith', notes: 'Normal results' },
    { date: '2025-01-15', type: 'X-Ray', provider: 'Dr. Jones', notes: 'Fracture healing' },
];

// Function to render the records into the table
function renderRecords() {
    recordEntries.innerHTML = '';
    records.forEach((record, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.type}</td>
            <td>${record.provider}</td>
            <td>${record.notes}</td>
            <td><button onclick="deleteRecord(${index})">Delete</button></td>
        `;
        recordEntries.appendChild(row);
    });
}

// Function to delete a record
function deleteRecord(index) {
    records.splice(index, 1);
    renderRecords();
}

// Add new record (dummy record for now)
addRecordBtn.addEventListener('click', () => {
    const newRecord = {
        date: new Date().toISOString().split('T')[0],
        type: 'Checkup',
        provider: 'Dr. John Doe',
        notes: 'General health check'
    };
    records.push(newRecord);
    renderRecords();
});

// View drafts (Placeholder functionality)
viewDraftsBtn.addEventListener('click', () => {
    alert('Viewing drafts... Feature to be implemented.');
});

// View historical records (Placeholder functionality)
viewHistoryBtn.addEventListener('click', () => {
    alert('Viewing historical records... Feature to be implemented.');
});

// Initial render of records
renderRecords();

