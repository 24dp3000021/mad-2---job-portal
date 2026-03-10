<template>
  <div class="container mt-4 pb-5">
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div><h4>Welcome {{ companyName }}</h4></div>
      <button @click="logout" class="btn btn-outline-danger btn-sm">logout</button>
    </div>

    <!-- Navigation Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button class="nav-link" :class="{active: view === 'drives'}" @click="view = 'drives'">My Drives</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{active: view === 'create'}" @click="openCreateForm()">Create New Drive</button>
      </li>
    </ul>

    <!-- VIEW 1: MANAGE DRIVES -->
    <div v-if="view === 'drives'">
      
      <!-- Search Bar -->
      <div class="mb-3 d-flex justify-content-end">
        <input v-model="searchQuery" type="text" class="form-control w-25" placeholder="Search Drive Title...">
      </div>

      <div class="card shadow-sm mb-4">
        <div class="card-header bg-primary text-white">Upcoming / Active Drives</div>
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr><th>Drive Title</th><th>Deadline</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="drive in filteredActiveDrives" :key="drive.id">
              <td>{{ drive.title }}</td>
              <td>{{ drive.deadline }}</td>
              <td><span class="badge bg-warning text-dark">{{ drive.status }}</span></td>
              <td>
                <button @click="viewApplications(drive)" class="btn btn-sm btn-info me-2">Applications</button>
                <button @click="openEditForm(drive)" class="btn btn-sm btn-secondary me-2">Edit</button>
                <button @click="markComplete(drive.id)" class="btn btn-sm btn-success me-2">Mark Complete</button>
                <button @click="deleteDrive(drive.id)" class="btn btn-sm btn-danger">Delete</button>
              </td>
            </tr>
            <tr v-if="filteredActiveDrives.length === 0"><td colspan="4" class="text-center text-muted">No active drives found.</td></tr>
          </tbody>
        </table>
      </div>

      <div class="card shadow-sm">
        <div class="card-header bg-secondary text-white">Closed Drives</div>
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr><th>Drive Title</th><th>Deadline</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="drive in filteredClosedDrives" :key="drive.id">
              <td>{{ drive.title }}</td>
              <td>{{ drive.deadline }}</td>
              <td>
                <button @click="viewApplications(drive)" class="btn btn-sm btn-info me-2">View Results</button>
                <button @click="deleteDrive(drive.id)" class="btn btn-sm btn-danger">Delete</button>
              </td>
            </tr>
            <tr v-if="filteredClosedDrives.length === 0"><td colspan="3" class="text-center text-muted">No closed drives found.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- VIEW 2: CREATE / EDIT DRIVE FORM -->
    <div v-if="view === 'create' || view === 'edit'" class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow p-4">
          <h4 class="mb-4">{{ view === 'edit' ? 'Edit Drive' : 'Create Placement Drive' }}</h4>
          <form @submit.prevent="submitDrive">
            <div class="mb-3">
              <label>Job Title</label>
              <input v-model="form.job_title" type="text" class="form-control" required>
            </div>
            <div class="mb-3">
              <label>Job Description</label>
              <textarea v-model="form.description" class="form-control" rows="3" required></textarea>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label>Minimum CGPA</label>
                <input v-model="form.min_cgpa" type="number" step="0.01" class="form-control" required>
              </div>
              <div class="col-md-6 mb-3">
                <label>Application Deadline</label>
                <input v-model="form.deadline" type="date" :min="today" class="form-control" required>
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label>Salary (LPA/CTC)</label>
                <input v-model="form.salary" type="text" class="form-control">
              </div>
              <div class="col-md-6 mb-3">
                <label>Location</label>
                <input v-model="form.location" type="text" class="form-control">
              </div>
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary w-100">{{ view === 'edit' ? 'Update Drive' : 'Create Drive' }}</button>
              <button type="button" @click="view = 'drives'" class="btn btn-secondary w-100">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- VIEW 3: VIEW APPLICATIONS -->
    <div v-if="view === 'applications'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Applications for: <span class="text-primary">{{ selectedDrive.title }}</span></h4>
        <button @click="view = 'drives'" class="btn btn-outline-secondary btn-sm">Back to Drives</button>
      </div>

      <div class="card shadow-sm">
        <table class="table table-bordered mb-0 text-center align-middle">
          <thead class="table-light">
            <tr>
              <th>Student Name</th>
              <th>CGPA</th>
              <th>Resume</th>
              <th>Status</th>
              <th>Update Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.id">
              <td>{{ app.student_name }}</td>
              <td>{{ app.cgpa }}</td>
              <td><a :href="app.resume" target="_blank" v-if="app.resume">View Resume</a><span v-else>-</span></td>
              <td><span class="badge" :class="app.status === 'Selected' ? 'bg-success' : (app.status === 'Rejected' ? 'bg-danger' : 'bg-warning text-dark')">{{ app.status }}</span></td>
              <td>
                <select v-model="app.newStatus" class="form-select form-select-sm d-inline-block w-auto me-2">
                  <option disabled value="">Select Status...</option>
                  <option value="Shortlisted">Shortlist</option>
                  <option value="Selected">Select</option>
                  <option value="Waiting">Waiting</option>
                  <option value="Rejected">Reject</option>
                </select>
                <button @click="updateAppStatus(app.id, app.newStatus)" class="btn btn-sm btn-primary" :disabled="!app.newStatus">Save</button>
              </td>
            </tr>
            <tr v-if="applications.length === 0"><td colspan="5" class="text-muted py-3">No applications received yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      view: 'drives',
      searchQuery: '',
      userId: null,
      companyName: '',
      drives:[],
      applications:[],
      selectedDrive: null,
      today: new Date().toISOString().split('T')[0],
      form: { id: null, job_title: '', description: '', min_cgpa: '', salary: '', location: '', deadline: '' }
    }
  },
  computed: {
    filteredActiveDrives() {
      return this.drives.filter(d => d.status !== 'Closed' && d.title.toLowerCase().includes(this.searchQuery.toLowerCase()));
    },
    filteredClosedDrives() {
      return this.drives.filter(d => d.status === 'Closed' && d.title.toLowerCase().includes(this.searchQuery.toLowerCase()));
    }
  },
  methods: {
    async loadDrives() {
      this.userId = localStorage.getItem('user_id');
      this.companyName = localStorage.getItem('name') || 'Organization';
      try {
        const res = await axios.get(`http://localhost:5000/api/company/drives/${this.userId}`);
        this.drives = res.data;
      } catch (err) {
        console.error("Error loading drives", err);
      }
    },
    openCreateForm() {
      this.form = { id: null, job_title: '', description: '', min_cgpa: '', salary: '', location: '', deadline: '' };
      this.view = 'create';
    },
    openEditForm(drive) {
      this.form = { 
        id: drive.id, 
        job_title: drive.title, 
        description: drive.description, 
        min_cgpa: drive.min_cgpa, 
        salary: drive.salary, 
        location: drive.location, 
        deadline: drive.deadline 
      };
      this.view = 'edit';
    },
    async submitDrive() {
      try {
        if (this.view === 'create') {
          await axios.post(`http://localhost:5000/api/company/drives/${this.userId}`, this.form);
          alert('Drive created successfully!');
        } else {
          await axios.put(`http://localhost:5000/api/company/drive/${this.form.id}`, this.form);
          alert('Drive updated successfully!');
        }
        this.loadDrives();
        this.view = 'drives';
      } catch (err) {
        alert(err.response?.data?.message || "Action failed");
      }
    },
    async deleteDrive(drive_id) {
      if(!confirm("Are you sure you want to completely delete this drive and all its applications?")) return;
      try {
        await axios.delete(`http://localhost:5000/api/company/drive/${drive_id}`);
        alert("Drive Deleted");
        this.loadDrives();
      } catch (err) {
        alert("Error deleting drive");
      }
    },
    async markComplete(drive_id) {
      if(!confirm("Marking as complete will close this drive. Students will no longer see it or be able to apply. Continue?")) return;
      try {
        await axios.put(`http://localhost:5000/api/company/drive/${drive_id}`, { status: 'Closed' });
        this.loadDrives();
      } catch (err) {
        alert("Error closing drive");
      }
    },
    async viewApplications(drive) {
      this.selectedDrive = drive;
      try {
        const res = await axios.get(`http://localhost:5000/api/drive/${drive.id}/applications`);
        this.applications = res.data.map(app => ({ ...app, newStatus: '' }));
        this.view = 'applications';
      } catch (err) {
        console.error(err);
      }
    },
    async updateAppStatus(appId, newStatus) {
      try {
        await axios.post(`http://localhost:5000/api/application/status`, { application_id: appId, status: newStatus });
        alert(`Status updated to ${newStatus}`);
        this.viewApplications(this.selectedDrive); // Refresh list
      } catch (err) {
        alert("Failed to update status");
      }
    },
    logout() {
      localStorage.clear();
      this.$router.push('/');
    }
  },
  mounted() {
    this.loadDrives();
  }
}
</script>