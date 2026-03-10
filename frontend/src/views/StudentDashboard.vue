<template>
  <div class="container mt-4 pb-5">
    <!-- NAVBAR (Wireframe Top Bar) -->
    <div class="d-flex justify-content-between border-bottom pb-2 mb-4 align-items-center">
      <div>
        <h4 class="mb-0">
          Welcome {{ profile.name || backupName }} 
          <span class="badge ms-2" :class="profile.active ? 'bg-success' : 'bg-danger'">
            {{ profile.active ? 'Active' : 'Inactive' }}
          </span>
        </h4>
      </div>
      <div class="nav-links">
        <button @click="view = 'home'" class="btn btn-link text-dark text-decoration-none">Home</button> |
        <button @click="view = 'profile'" class="btn btn-link text-dark text-decoration-none">Edit Profile</button> |
        <button @click="view = 'history'" class="btn btn-link text-dark text-decoration-none">History</button> |
        <button @click="logout" class="btn btn-link text-danger text-decoration-none">Logout</button>
      </div>
    </div>

    <!-- TRACKING DASHBOARD (Real-Time Stats) -->
    <div v-if="view === 'home' || view === 'history'" class="row text-center mb-4 g-2">
      <div class="col-md-3">
        <div class="card bg-primary text-white p-2 shadow-sm border-0">
          <h6 class="small mb-1">Total Applied</h6>
          <h3>{{ trackingStats.total }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-dark p-2 shadow-sm border-0">
          <h6 class="small mb-1">Shortlisted</h6>
          <h3>{{ trackingStats.shortlisted }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white p-2 shadow-sm border-0">
          <h6 class="small mb-1">Selected</h6>
          <h3>{{ trackingStats.selected }}</h3>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-danger text-white p-2 shadow-sm border-0">
          <h6 class="small mb-1">Rejected</h6>
          <h3>{{ trackingStats.rejected }}</h3>
        </div>
      </div>
    </div>

    <!-- VIEW 1: HOME (Organizations & Search) -->
    <div v-if="view === 'home'">
      <div class="row mb-4">
        <div class="col-md-6">
          <label class="small text-muted">Search Company</label>
          <input v-model="search" class="form-control" placeholder="Type company name...">
        </div>
        <div class="col-md-6">
          <label class="small text-muted">Eligibility Filter (Max Min-CGPA)</label>
          <input v-model.number="cgpaLimit" type="number" step="0.1" class="form-control" placeholder="e.g. 7.5">
        </div>
      </div>

      <h6 class="text-muted mb-3 border-bottom pb-1">Organizations</h6>
      <div v-if="filteredCompanies.length === 0" class="alert alert-light border text-center">No organizations found matching your search.</div>
      <div v-for="org in filteredCompanies" :key="org.id" class="card mb-2 shadow-sm border-0">
        <div class="card-body d-flex justify-content-between align-items-center py-2">
          <span class="fw-bold">{{ org.name }}</span>
          <button @click="showDrives(org.id)" class="btn btn-primary btn-sm px-3">view details</button>
        </div>
      </div>

      <div class="mt-5">
        <h6 class="text-muted mb-3 border-bottom pb-1">Recent Applied Drives (Summary)</h6>
        <table class="table table-bordered bg-white shadow-sm align-middle text-center">
          <thead class="table-light">
            <tr><th>Sr No.</th><th>Drive Name</th><th>Company</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="(app, idx) in history.slice(0, 3)" :key="idx">
              <td>{{ idx + 1 }}</td>
              <td>{{ app.drive_title }}</td>
              <td>{{ app.company }}</td>
              <td><button @click="view = 'history'" class="btn btn-outline-primary btn-sm px-3">view details</button></td>
            </tr>
            <tr v-if="history.length === 0"><td colspan="4" class="text-muted">Apply to jobs to see your summary here.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- VIEW 2: PROFILE (CRITICAL FIX FOR 0 CGPA) -->
    <div v-if="view === 'profile'" class="row justify-content-center">
      <div class="col-md-6 card shadow p-4 border-0">
        <h5 class="mb-4 text-center border-bottom pb-2">Edit Detailed Profile</h5>
        <div class="mb-3">
          <label class="small fw-bold">Full Name</label>
          <input v-model="profile.name" class="form-control" disabled>
        </div>
        <div class="mb-3">
          <label class="small fw-bold">Department</label>
          <select v-model="profile.department" class="form-select">
            <option value="Computer Science">Computer Science</option>
            <option value="Electrical">Electrical</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electronics">Electronics</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="small fw-bold">Current CGPA (Update this to enable applying)</label>
          <input v-model.number="profile.cgpa" type="number" step="0.01" class="form-control">
        </div>
        <div class="mb-3">
          <label class="small fw-bold">Resume Link (PDF URL)</label>
          <input v-model="profile.resume" class="form-control" placeholder="Google Drive / Dropbox link">
        </div>
        <button @click="updateProfile" class="btn btn-success w-100 mt-2">Save Profile & Refresh Status</button>
        <button @click="view = 'home'" class="btn btn-link w-100 mt-2 text-dark">Cancel</button>
      </div>
    </div>

    <!-- VIEW 3: DRIVE LIST (For specific Org) -->
    <div v-if="view === 'drive_list'">
      <div class="d-flex justify-content-between mb-3 align-items-center">
        <button @click="view = 'home'" class="btn btn-sm btn-secondary">← Back to Organizations</button>
        <input v-model="jobSearch" class="form-control w-25" placeholder="Filter jobs...">
      </div>
      <div v-for="d in filteredOrgDrives" :key="d.id" class="card mb-2 p-3 border-start border-4 shadow-sm" :class="d.is_expired ? 'border-danger' : 'border-success'">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h5 class="mb-0 text-primary">{{ d.title }}</h5>
            <small class="text-muted">Min CGPA required: {{ d.min_cgpa }} | Status: <strong>{{ d.is_expired ? 'CLOSED' : 'OPEN' }}</strong></small>
          </div>
          <button @click="openDetails(d)" class="btn btn-primary btn-sm px-3">view details</button>
        </div>
      </div>
    </div>

    <!-- VIEW 4: DRIVE DETAILS & APPLY -->
    <div v-if="view === 'details'" class="card shadow p-4 border-0 mx-auto" style="max-width: 850px;">
        <div class="d-flex justify-content-between align-items-start">
          <div class="col-8">
            <h2 class="text-primary">{{ selectedDrive.title }}</h2>
            <h5 class="text-muted mb-4">{{ selectedDrive.company_name }}</h5>
            <h6>Job Description:</h6>
            <p class="text-secondary">{{ selectedDrive.description }}</p>
            <hr>
            <p><strong>Salary Package:</strong> {{ selectedDrive.salary }}</p>
            <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
            <p><strong>Min CGPA Criteria:</strong> {{ selectedDrive.min_cgpa }}</p>
          </div>
          <div class="col-4 text-center">
            <div class="rounded-circle bg-light border d-flex align-items-center justify-content-center mx-auto mb-2" style="width:100px; height:100px; font-size: 12px; color: #aaa;">LOGO</div>
            <p class="small text-muted mb-0">Deadline</p>
            <p class="fw-bold text-danger">{{ selectedDrive.deadline }}</p>
          </div>
        </div>
        <div class="mt-4 border-top pt-3 d-flex gap-2">
          <button @click="apply(selectedDrive.id)" 
                  class="btn btn-primary px-5" 
                  :disabled="hasApplied(selectedDrive.id) || selectedDrive.is_expired || profile.cgpa < selectedDrive.min_cgpa">
            {{ getBtnText(selectedDrive) }}
          </button>
          <button @click="view = 'drive_list'" class="btn btn-outline-secondary px-4">Go Back</button>
        </div>
    </div>

    <!-- VIEW 5: HISTORY PAGE -->
    <div v-if="view === 'history'" class="card shadow p-4 border-0">
      <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
        <div>
          <h4 class="mb-0">Student Application History</h4>
          <p class="small text-muted mb-0">Student: {{ profile.name }} | Dept: {{ profile.department }}</p>
        </div>
        <button @click="view = 'home'" class="btn btn-sm btn-outline-primary px-4">Back to Dashboard</button>
      </div>
      <table class="table table-hover text-center align-middle border shadow-sm">
        <thead class="table-light">
          <tr><th>No.</th><th>Job Title</th><th>Company</th><th>Date Applied</th><th>Status</th><th>Remark</th></tr>
        </thead>
        <tbody>
          <tr v-for="(a, idx) in history" :key="a.drive_id">
            <td>{{ idx + 1 }}</td>
            <td class="fw-bold">{{ a.drive_title }}</td>
            <td>{{ a.company }}</td>
            <td>{{ a.date }}</td>
            <td>
              <span class="badge px-3 py-2" :class="getBadgeClass(a.status)">{{ a.status }}</span>
            </td>
            <td class="small text-muted">None</td>
          </tr>
          <tr v-if="history.length === 0"><td colspan="6" class="py-5 text-muted">No application history found. Search for jobs on the home page to apply!</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      view: 'home',
      search: '',
      cgpaLimit: null,
      jobSearch: '',
      profile: { name: '', cgpa: 0, active: true, department: '', is_blacklisted: false },
      companies: [],
      drives: [],
      history: [],
      selectedOrgId: null,
      selectedDrive: {},
      userId: null,
      backupName: localStorage.getItem('name')
    }
  },
  computed: {
    filteredCompanies() {
      return this.companies.filter(c => c.name.toLowerCase().includes(this.search.toLowerCase()))
    },
    filteredOrgDrives() {
      return this.drives.filter(d => 
        d.company_id === this.selectedOrgId && 
        (this.cgpaLimit ? d.min_cgpa <= this.cgpaLimit : true) &&
        d.title.toLowerCase().includes(this.jobSearch.toLowerCase())
      )
    },
    trackingStats() {
      return {
        total: this.history.length,
        shortlisted: this.history.filter(a => a.status === 'Shortlisted' || a.status === 'Selected').length,
        selected: this.history.filter(a => a.status === 'Selected').length,
        rejected: this.history.filter(a => a.status === 'Rejected').length
      }
    }
  },
  methods: {
    async loadData() {
      this.userId = localStorage.getItem('user_id'); // Persistent ID fetch
      if (!this.userId) {
        this.$router.push('/');
        return;
      }
      try {
        const [p, c, h, d] = await Promise.all([
          axios.get(`http://localhost:5000/api/student/profile/${this.userId}`),
          axios.get(`http://localhost:5000/api/student/companies`),
          axios.get(`http://localhost:5000/api/student/history/${this.userId}`),
          axios.get(`http://localhost:5000/api/student/drives`)
        ]);
        this.profile = p.data;
        this.companies = c.data;
        this.history = h.data;
        this.drives = d.data;
      } catch (err) {
        console.log("Fetch failed. User might have been logged out manually.");
      }
    },
    showDrives(id) {
      this.selectedOrgId = id;
      this.view = 'drive_list';
    },
    openDetails(d) {
      this.selectedDrive = d;
      this.view = 'details';
    },
    hasApplied(id) {
      return this.history.some(a => a.drive_id === id)
    },
    getBtnText(d) {
      if (this.hasApplied(d.id)) return 'Applied';
      if (d.is_expired) return 'Closed';
      if (this.profile.cgpa < d.min_cgpa) return 'Ineligible';
      return 'Apply';
    },
    getBadgeClass(s) {
      if (s === 'Selected') return 'bg-success';
      if (s === 'Rejected') return 'bg-danger';
      if (s === 'Shortlisted' || s === 'Waiting') return 'bg-warning text-dark';
      return 'bg-info text-dark';
    },
    async updateProfile() {
      try {
        await axios.put(`http://localhost:5000/api/student/profile/${this.userId}`, this.profile);
        alert("Profile Saved successfully!");
        await this.loadData(); // Sync with backend
        this.view = 'home';
      } catch (e) { alert("Failed to update profile."); }
    },
    async apply(id) {
      if (!this.profile.active) { alert("Account inactive. Contact Admin."); return; }
      try {
        const res = await axios.post(`http://localhost:5000/api/student/apply`, { user_id: this.userId, drive_id: id });
        alert(res.data.message);
        await this.loadData(); // Refresh history immediately
        this.view = 'history'; // Send to history to confirm status
      } catch (err) {
        alert(err.response?.data?.message || "Error applying.");
      }
    },
    logout() {
      localStorage.clear();
      this.$router.push('/');
    }
  },
  mounted() {
    this.loadData();
  }
}
</script>