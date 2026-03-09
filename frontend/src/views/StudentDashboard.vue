<template>
  <div class="container mt-4 pb-5">
    <!-- NAVBAR -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div>
        <h4 class="mb-0">Welcome {{ profile.name }}</h4>
        <small>
          <strong>Profile Status: </strong> 
          <span class="badge" :class="profile.is_blacklisted ? 'bg-danger' : 'bg-success'">
            {{ profile.is_blacklisted ? 'Blacklisted / Inactive' : 'Active' }}
          </span>
        </small>
      </div>
      <div class="nav-links">
        <button @click="view = 'home'" class="btn btn-link text-dark">Home</button> |
        <button @click="view = 'profile'" class="btn btn-link text-dark">Edit Profile</button> |
        <button @click="view = 'history'" class="btn btn-link text-dark">History</button> |
        <button @click="logout" class="btn btn-link text-danger">Logout</button>
      </div>
    </div>

    <!-- VIEW 1: MAIN DASHBOARD -->
    <div v-if="view === 'home'">
      
      <!-- Real-Time Application Tracking Stats -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white text-center p-3 shadow-sm">
            <h6>Total Applied</h6><h3>{{ trackingStats.totalApplied }}</h3>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-dark text-center p-3 shadow-sm">
            <h6>Pending/In Review</h6><h3>{{ trackingStats.pending }}</h3>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white text-center p-3 shadow-sm">
            <h6>Shortlisted</h6><h3>{{ trackingStats.shortlisted }}</h3>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-danger text-white text-center p-3 shadow-sm">
            <h6>Rejected</h6><h3>{{ trackingStats.rejected }}</h3>
          </div>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="text-muted mb-0">All Placement Drives</h5>
        <input v-model="searchQuery" type="text" class="form-control w-25 shadow-sm" placeholder="Search Drive or Company...">
      </div>

      <!-- Drives List -->
      <div class="row">
        <div class="col-12 mb-5">
          <div v-for="drive in filteredDrives" :key="drive.id" class="card mb-2 border shadow-sm">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-1 text-primary">{{ drive.title }}</h5>
                <span class="text-muted">{{ drive.company_name }} | Deadline: <strong>{{ drive.deadline }}</strong></span>
              </div>
              <button @click="showDriveDetails(drive)" class="btn btn-outline-primary btn-sm px-3">View & Apply</button>
            </div>
          </div>
          <div v-if="filteredDrives.length === 0" class="text-center text-muted mt-4">
            No placement drives found matching your search.
          </div>
        </div>
      </div>
    </div>

    <!-- VIEW 2: EDIT PROFILE -->
    <div v-if="view === 'profile'" class="row justify-content-center">
      <div class="col-md-6 card shadow p-4">
        <h5>Edit Detailed Profile</h5>
        <div class="mb-3"><label>Full Name</label><input v-model="profile.name" class="form-control" disabled></div>
        <div class="mb-3">
            <label>Department</label>
            <select v-model="profile.department" class="form-select">
                <option>Computer Science</option><option>Electronics</option><option>Mechanical</option>
            </select>
        </div>
        <div class="mb-3"><label>CGPA</label><input v-model="profile.cgpa" type="number" step="0.01" class="form-control"></div>
        <div class="mb-3"><label>Resume Link (File Path)</label><input v-model="profile.resume" type="text" class="form-control" placeholder="Upload path/URL"></div>
        <button @click="updateProfile" class="btn btn-primary w-100">Save Changes</button>
        <button @click="view = 'home'" class="btn btn-link w-100 mt-2">Back to Dashboard</button>
      </div>
    </div>

    <!-- VIEW 3: DRIVE DETAILS -->
    <div v-if="view === 'drive_details'" class="row justify-content-center">
      <div class="col-md-8 card shadow p-4">
        <div class="d-flex justify-content-between">
            <div>
                <h3 class="text-primary">{{ selectedDrive.title }}</h3>
                <h5 class="text-muted">{{ selectedDrive.company_name }}</h5>
                <p class="mt-4">{{ selectedDrive.description }}</p>
                <p><strong>Min CGPA Required:</strong> {{ selectedDrive.min_cgpa }}</p>
                <p><strong>Salary:</strong> {{ selectedDrive.salary || 'Competitive' }}</p>
                <p><strong>Location:</strong> {{ selectedDrive.location || 'Remote' }}</p>
                <p><strong>Deadline:</strong> <span class="text-danger">{{ selectedDrive.deadline }}</span></p>
            </div>
            <div class="text-center">
                <div class="rounded-circle bg-info mb-2" style="width:80px; height:80px; margin:auto"></div>
                <small>LOGO</small>
            </div>
        </div>
        
        <div class="mt-4 border-top pt-3 d-flex gap-2 align-items-center">
            <template v-if="!canApply(selectedDrive).allowed">
                <div class="alert alert-warning mb-0 w-100">
                    <strong>Cannot Apply: </strong> {{ canApply(selectedDrive).reason }}
                </div>
            </template>
            <template v-else>
                <button @click="apply(selectedDrive.id)" class="btn btn-success px-5">Submit Application</button>
            </template>
            <button @click="view = 'home'" class="btn btn-outline-secondary px-4">Go Back</button>
        </div>
      </div>
    </div>

    <!-- VIEW 4: HISTORY -->
    <div v-if="view === 'history'">
      <div class="card shadow p-4 border-0">
        <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
                <h4>Student Application History</h4>
                <p class="mb-0"><strong>Student Name:</strong> {{ profile.name }}</p>
                <p><strong>Department:</strong> {{ profile.department }}</p>
            </div>
            <button @click="view = 'home'" class="btn btn-outline-primary btn-sm">Back to Home</button>
        </div>
        <table class="table table-bordered text-center align-middle">
            <thead class="table-light">
                <tr><th>No.</th><th>Job Title</th><th>Company</th><th>Date Applied</th><th>Status</th></tr>
            </thead>
            <tbody>
                <tr v-for="(app, index) in history" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>{{ app.drive_title }}</td>
                    <td>{{ app.company }}</td>
                    <td>{{ app.date }}</td>
                    <td>
                      <span class="badge" 
                            :class="{'bg-success': app.status === 'Selected' || app.status === 'Shortlisted', 
                                     'bg-warning text-dark': app.status === 'Applied' || app.status === 'Pending', 
                                     'bg-danger': app.status === 'Rejected'}">
                        {{ app.status }}
                      </span>
                    </td>
                </tr>
                <tr v-if="history.length === 0">
                  <td colspan="5" class="text-muted">You have not applied to any companies yet.</td>
                </tr>
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
      view: 'home',
      searchQuery: '',
      profile: { name: '', cgpa: 0, resume: '', department: '', is_blacklisted: false },
      companies:[],
      drives: [],
      history:[],
      selectedDrive: {},
      userId: null // FIX 1: Null by default. Fetched cleanly on mount.
    }
  },
  computed: {
    filteredDrives() {
      if (!this.searchQuery) return this.drives;
      const q = this.searchQuery.toLowerCase();
      return this.drives.filter(d => 
        d.title.toLowerCase().includes(q) || 
        d.company_name.toLowerCase().includes(q)
      );
    },
    // Tracking stats now perfectly match the history!
    trackingStats() {
      let stats = { totalApplied: this.history.length, pending: 0, shortlisted: 0, rejected: 0 };
      this.history.forEach(app => {
        const st = app.status.toLowerCase();
        if (st === 'applied' || st === 'pending') stats.pending++;
        if (st === 'shortlisted' || st === 'selected') stats.shortlisted++;
        if (st === 'rejected') stats.rejected++;
      });
      return stats;
    }
  },
  methods: {
    async loadData() {
      try {
        const[p, c, h, d] = await Promise.all([
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
        console.error("Error fetching data. Make sure backend is running:", err);
      }
    },
    showDriveDetails(drive) {
        this.selectedDrive = drive;
        this.view = 'drive_details';
    },
    canApply(drive) {
        if (this.profile.is_blacklisted) {
            return { allowed: false, reason: "Your profile is blacklisted by the Admin." };
        }
        
        const today = new Date().toISOString().split('T')[0];
        if (drive.deadline < today) {
            return { allowed: false, reason: "The application deadline has passed." };
        }
        
        if (parseFloat(this.profile.cgpa) < parseFloat(drive.min_cgpa)) {
            return { allowed: false, reason: `Minimum CGPA of ${drive.min_cgpa} is required. Your CGPA is ${this.profile.cgpa}.` };
        }
        
        const alreadyApplied = this.history.find(h => h.drive_title === drive.title && h.company === drive.company_name);
        if (alreadyApplied) {
            return { allowed: false, reason: "You have already applied for this drive." };
        }
        
        return { allowed: true, reason: "" };
    },
    async updateProfile() {
      await axios.put(`http://localhost:5000/api/student/profile/${this.userId}`, { 
          cgpa: this.profile.cgpa, resume_link: this.profile.resume, department: this.profile.department 
      });
      alert("Profile Saved!");
      this.loadData();
      this.view = 'home';
    },
    async apply(id) {
      try {
        await axios.put(`http://localhost:5000/api/student/profile/${this.userId}`, { cgpa: this.profile.cgpa });
        const res = await axios.post(`http://localhost:5000/api/student/apply`, { user_id: this.userId, drive_id: id });
        alert(res.data.message);
        this.loadData();
        this.view = 'home';
      } catch (err) { 
        alert(err.response.data.message); 
      }
    },
    logout() { 
        localStorage.clear(); 
        this.$router.push('/'); 
    }
  },
  mounted() { 
      // FIX 1: Safely fetch the ID *after* the component loads to fix blank screen
      this.userId = localStorage.getItem('user_id');
      if (this.userId) {
          this.loadData(); 
      } else {
          this.$router.push('/');
      }
  }
}
</script>